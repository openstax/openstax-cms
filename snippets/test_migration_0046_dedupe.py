"""
Migration test: prove that snippets 0046 self-heals duplicate rows.

Uses MigrationExecutor to:
  1. Roll back to 0045 (no constraints).
  2. Insert intentional duplicates.
  3. Close and reopen the DB connection so any pending PostgreSQL trigger events
     are flushed before DDL runs.
  4. Migrate forward to 0046 (RunPython heal + AddConstraints).
  5. Assert:
       a. FacultyResource (text-field path): both rows survive, the extra one
          gets a " (dup <pk>)" suffix.  A third row with the original heading
          then violates the new constraint (IntegrityError).
       b. ContentWarning (singleton/locale-only path): the extra row is deleted,
          only the lowest-pk row survives.
  6. Roll back to latest so no DB-state bleed.

Models used:
  - Case 1 (rename path): FacultyResource  — constraint (heading, locale)
  - Case 2 (delete path): ContentWarning   — constraint (locale,)  [singleton]
"""

from django.db import connection, IntegrityError
from django.test import TransactionTestCase
from django.db.migrations.executor import MigrationExecutor


TARGET = ("snippets", "0046_amazonbookblurb_unique_amazonbookblurb_per_locale_and_more")
ROLLBACK = ("snippets", "0045_delete_givebanner")


def _fresh_executor():
    """Return a MigrationExecutor with a fresh connection state."""
    # Close any open connection so PostgreSQL starts a clean transaction with
    # no pending trigger events before we do DDL (AddConstraint).
    connection.close()
    executor = MigrationExecutor(connection)
    executor.loader.check_consistent_history(connection)
    return executor


class Migration0046DedupeTest(TransactionTestCase):
    """Proves the 0046 RunPython heal step works for both the rename and delete paths."""

    databases = {"default"}

    def setUp(self):
        # Roll the DB back to 0045 so there are no per-locale constraints yet.
        executor = _fresh_executor()
        executor.migrate([ROLLBACK])

    def tearDown(self):
        # Always restore to latest so subsequent test runs see a fully-migrated DB.
        executor = _fresh_executor()
        leaf_nodes = executor.loader.graph.leaf_nodes()
        executor.migrate(leaf_nodes)

    def _get_locale(self, apps):
        """Return (or create) the default English locale via the given historical apps."""
        Locale = apps.get_model("wagtailcore", "Locale")
        locale, _ = Locale.objects.get_or_create(language_code="en")
        return locale

    # ------------------------------------------------------------------
    # Case 1: text-field rename path (FacultyResource, constraint heading+locale)
    # ------------------------------------------------------------------
    def test_text_field_rename_path(self):
        # Get historical model state at 0045 (no constraints).
        state_at_0045 = _fresh_executor().loader.project_state([ROLLBACK])
        apps = state_at_0045.apps
        FacultyResource = apps.get_model("snippets", "FacultyResource")
        locale = self._get_locale(apps)

        heading = "Instructor Answer Guide"

        # Insert two rows with the same heading + locale — valid at 0045 (no constraint).
        row_a = FacultyResource.objects.create(heading=heading, locale=locale)
        row_b = FacultyResource.objects.create(heading=heading, locale=locale)
        self.assertLess(row_a.pk, row_b.pk)

        # Close the connection so PostgreSQL clears any pending trigger events
        # before AddConstraint DDL runs inside executor.migrate().
        connection.close()

        # --- Migrate forward to 0046 ---
        executor2 = _fresh_executor()
        executor2.migrate([TARGET])

        state_at_0046 = executor2.loader.project_state([TARGET])
        apps2 = state_at_0046.apps
        FacultyResource2 = apps2.get_model("snippets", "FacultyResource")
        # Re-fetch locale from the 0046-state apps so model identity matches.
        locale2 = self._get_locale(apps2)

        # Both rows must still exist (rename path, not delete).
        rows = list(FacultyResource2.objects.filter(pk__in=[row_a.pk, row_b.pk]))
        self.assertEqual(
            len(rows), 2,
            "Both FacultyResource rows should survive the rename path",
        )

        by_pk = {r.pk: r for r in rows}

        # The lower-pk row keeps the original heading.
        self.assertEqual(by_pk[row_a.pk].heading, heading)

        # The higher-pk row has a " (dup <pk>)" suffix.
        self.assertIn(
            "(dup", by_pk[row_b.pk].heading,
            "Extra row heading should contain '(dup' suffix after heal",
        )

        # The new constraint is now enforced: a third row with the original
        # heading + locale must raise IntegrityError.
        with self.assertRaises(IntegrityError):
            FacultyResource2.objects.create(heading=heading, locale=locale2)

    # ------------------------------------------------------------------
    # Case 2: singleton/locale-only delete path (ContentWarning, constraint locale)
    # ------------------------------------------------------------------
    def test_locale_only_delete_path(self):
        # Get historical model state at 0045 (no constraints).
        state_at_0045 = _fresh_executor().loader.project_state([ROLLBACK])
        apps = state_at_0045.apps
        ContentWarning = apps.get_model("snippets", "ContentWarning")
        locale = self._get_locale(apps)

        # Insert two ContentWarning rows for the same locale — no constraint yet at 0045.
        cw_a = ContentWarning.objects.create(content_warning="Warning text A", locale=locale)
        cw_b = ContentWarning.objects.create(content_warning="Warning text B", locale=locale)
        self.assertLess(cw_a.pk, cw_b.pk)

        # Close the connection so PostgreSQL clears any pending trigger events
        # before AddConstraint DDL runs inside executor.migrate().
        connection.close()

        # --- Migrate forward to 0046 ---
        executor2 = _fresh_executor()
        executor2.migrate([TARGET])

        state_at_0046 = executor2.loader.project_state([TARGET])
        apps2 = state_at_0046.apps
        ContentWarning2 = apps2.get_model("snippets", "ContentWarning")

        # Only the lowest-pk row should remain (singleton delete path).
        surviving_pks = list(
            ContentWarning2.objects
            .filter(pk__in=[cw_a.pk, cw_b.pk])
            .values_list("pk", flat=True)
        )
        self.assertEqual(
            surviving_pks, [cw_a.pk],
            "Only the lowest-pk ContentWarning row should survive the delete path",
        )
