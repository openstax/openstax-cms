"""
Fix up data after restoring a non-prod database from a prod dump.

Run this AFTER pg_dump/restore and S3 bucket sync have completed. It:

  1. Updates the Wagtail Site hostname so URL routing matches the target env.
  2. Rewrites prod URLs (`https://openstax.org`, `//openstax.org`, etc.) in
     RichText, StreamField, URLField, and string-typed fields across every
     concrete model in the project.
  3. Rewrites the latest revision per Wagtail Page so the admin editor shows
     env-correct URLs rather than the prod ones from the dump.
  4. Empties Salesforce-synced data tables. Prod salesforce IDs reference
     prod's Salesforce instance, so they're useless on dev/staging. The next
     scheduled sync (update_partners / update_schools / etc.) repopulates
     them with the env-correct sandbox data. Local config tables
     (SalesforceSettings, SalesforceForms, *Mapping) are left alone.

User accounts are carried across by the dump/restore and left alone here —
the CMS auth_user table holds only internal staff, so engineers can log into
the refreshed env with their prod credentials.

Persistence is deliberately done with queryset `.update()` (and set-based
`Replace()` for text columns), never `instance.save()`. That is what keeps the
command safe to run against a freshly restored prod dataset: it never fires
`post_save` signals (which would issue CloudFront invalidations against prod's
distribution and send errata status emails to real submitters), never triggers
model `save()` overrides (Errata date re-stamping, Book → Salesforce lookups,
Book label propagation, NewsArticle pin cascades), never runs `full_clean()`,
and never re-indexes search per row. Rebuild the search index separately after
the refresh (see the runbook) if you use a non-database backend.

Dry-run by default. Refuses to run when ENVIRONMENT == 'prod'.

Idempotent: the URL patterns include a scheme or `//` prefix so a second
run does not double-rewrite (`https://dev.openstax.org` does not contain
the substring `https://openstax.org`), and the row pre-filter on `//<host>`
stops matching once a row has been rewritten.
"""
import json

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.db.models import F, Value
from django.db.models.functions import Cast, Replace

from wagtail.fields import StreamField
from wagtail.models import Page, Revision, Site


DEFAULT_SOURCE_HOST = 'openstax.org'

# RichTextField subclasses TextField and URLField subclasses CharField, so this
# pair covers all plain-text URL-bearing columns. StreamField is handled
# separately because its column is jsonb.
TEXT_FIELD_TYPES = (models.CharField, models.TextField)

SKIP_APP_LABELS = {
    'contenttypes',
    'sessions',
    'admin',
    'auth',
    'wagtail_transfer',
    # salesforce models are wiped wholesale by _truncate_salesforce_synced_data,
    # so there's no point doing URL rewriting in them first.
    'salesforce',
}

# Salesforce-synced data tables — emptied during fixup so the next scheduled
# sync repopulates with the target env's sandbox data. Config/mapping models
# (SalesforceSettings, SalesforceForms, *Mapping, MapBoxDataset) are NOT in
# this list and stay intact.
SALESFORCE_SYNCED_MODELS = [
    'salesforce.Adopter',
    'salesforce.AdoptionOpportunityRecord',
    'salesforce.School',
    'salesforce.Partner',
    'salesforce.ResourceDownload',
    'salesforce.SavingsNumber',
]


def _replacements(source_host, target_host):
    """Build (old, new) string pairs. Order: most-specific first."""
    return [
        (f'https://{source_host}', f'https://{target_host}'),
        (f'http://{source_host}', f'https://{target_host}'),
        (f'//{source_host}', f'//{target_host}'),
    ]


def _apply(value, replacements):
    """Apply all replacements to a string. Returns (new_value, changed?)."""
    if not isinstance(value, str):
        return value, False
    new = value
    for old, repl in replacements:
        new = new.replace(old, repl)
    return new, new != value


def _apply_json(data, replacements):
    """Apply replacements to a JSON-serializable structure. Returns (new, changed?)."""
    new_json, changed = _apply(json.dumps(data), replacements)
    if changed:
        return json.loads(new_json), True
    return data, False


class Command(BaseCommand):
    help = (
        "Fix up a non-prod database after restoring from a prod dump. "
        "Updates the Wagtail Site hostname and rewrites prod URLs in content. "
        "DRY RUN BY DEFAULT — pass --commit to apply."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--target-host',
            required=True,
            help="Hostname for this environment, e.g. dev.openstax.org",
        )
        parser.add_argument(
            '--source-host',
            default=DEFAULT_SOURCE_HOST,
            help=f"Hostname being replaced. Default: {DEFAULT_SOURCE_HOST}",
        )
        parser.add_argument(
            '--commit',
            action='store_true',
            help="Apply changes. Without this, runs in dry-run mode.",
        )

    def handle(self, *args, **options):
        target_host = options['target_host'].strip().lower()
        source_host = options['source_host'].strip().lower()
        commit = options['commit']

        if getattr(settings, 'ENVIRONMENT', None) == 'prod':
            raise CommandError("Refuse to run on production.")
        if target_host == source_host:
            raise CommandError(
                f"--target-host ({target_host}) cannot equal --source-host ({source_host})."
            )
        if '.' not in target_host:
            raise CommandError(f"Invalid --target-host: {target_host!r}")

        mode = self.style.WARNING('[COMMIT]') if commit else self.style.WARNING('[DRY RUN]')
        self.stdout.write(f"{mode} replacing {source_host} → {target_host}")

        replacements = _replacements(source_host, target_host)
        # Every rewritable occurrence (https://, http://, //) contains this
        # substring, so it is a precise, index-friendly row pre-filter.
        needle = f'//{source_host}'

        with transaction.atomic():
            self._update_site(target_host)
            self._rewrite_concrete_models(replacements, needle)
            self._rewrite_page_revisions(replacements, needle)
            self._truncate_salesforce_synced_data()
            if not commit:
                transaction.set_rollback(True)
                self.stdout.write(
                    self.style.WARNING("[DRY RUN] All changes rolled back. Pass --commit to apply.")
                )
            else:
                self.stdout.write(self.style.SUCCESS("Done."))

    def _update_site(self, target_host):
        try:
            site = Site.objects.get(is_default_site=True)
        except Site.DoesNotExist:
            self.stdout.write(self.style.WARNING("  no default Site found, skipping hostname update"))
            return
        old = site.hostname
        if old == target_host:
            self.stdout.write(f"  Site.hostname already {target_host}, no change")
            return
        # Site.save() only clears the root-paths cache; safe and desirable here.
        site.hostname = target_host
        site.save()
        self.stdout.write(f"  Site.hostname: {old} → {target_host}")

    def _rewrite_concrete_models(self, replacements, needle):
        """Rewrite URL-bearing fields across every concrete project model.

        Only each model's OWN (local) fields are touched, so multi-table
        inheritance rows are handled exactly once (the base Page pass rewrites
        title/slug/etc.; each subclass pass rewrites its own columns) and every
        UPDATE stays single-table.
        """
        for model in apps.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            if model._meta.app_label in SKIP_APP_LABELS:
                continue

            local_fields = model._meta.local_fields
            text_fields = [f for f in local_fields if isinstance(f, TEXT_FIELD_TYPES)]
            stream_fields = [f for f in local_fields if isinstance(f, StreamField)]

            for field in text_fields:
                self._rewrite_text_field(model, field, replacements, needle)
            for field in stream_fields:
                self._rewrite_stream_field(model, field, replacements, needle)

    def _rewrite_text_field(self, model, field, replacements, needle):
        """Set-based rewrite of one text/char column. No save(), no signals."""
        expr = F(field.name)
        for old, new in replacements:
            expr = Replace(expr, Value(old), Value(new))
        rows = model._base_manager.filter(
            **{f'{field.name}__contains': needle}
        ).update(**{field.name: expr})
        if rows:
            self.stdout.write(f"  {model._meta.label}.{field.name}: rewrote {rows} row(s)")

    def _rewrite_stream_field(self, model, field, replacements, needle):
        """Per-row rewrite of one jsonb StreamField column, persisted via update()."""
        candidates = (
            model._base_manager
            .annotate(_sf_text=Cast(field.name, output_field=models.TextField()))
            .filter(_sf_text__contains=needle)
        )
        count = 0
        for instance in candidates.iterator():
            value = getattr(instance, field.name)
            # StreamValue.raw_data is a RawDataView; materialize to a plain list
            # of block dicts so it round-trips through json.
            raw = list(value.raw_data) if hasattr(value, 'raw_data') else value
            new_raw, changed = _apply_json(raw, replacements)
            if not changed:
                continue
            # Round-trip through the descriptor so update() receives a value the
            # StreamField knows how to serialize; update() bypasses save().
            setattr(instance, field.name, new_raw)
            model._base_manager.filter(pk=instance.pk).update(
                **{field.name: getattr(instance, field.name)}
            )
            count += 1
        if count:
            self.stdout.write(f"  {model._meta.label}.{field.name}: rewrote {count} row(s)")

    def _rewrite_page_revisions(self, replacements, needle):
        """Rewrite the latest revision per page so the admin editor reflects new URLs.

        One query selects the latest revisions across all pages; the jsonb
        content is pre-filtered to those actually containing the source host.
        """
        latest_ids = list(
            Page.objects.exclude(latest_revision__isnull=True)
            .values_list('latest_revision_id', flat=True)
        )
        if not latest_ids:
            return
        candidates = (
            Revision.objects.filter(id__in=latest_ids)
            .annotate(_content_text=Cast('content', output_field=models.TextField()))
            .filter(_content_text__contains=needle)
        )
        count = 0
        for rev in candidates.iterator():
            content = rev.content
            if not content:
                continue
            new_content, changed = _apply_json(content, replacements)
            if changed:
                Revision.objects.filter(pk=rev.pk).update(content=new_content)
                count += 1
        if count:
            self.stdout.write(f"  wagtailcore.Revision: rewrote {count} latest revision(s)")

    def _truncate_salesforce_synced_data(self):
        """Empty Salesforce-synced data tables so the next sync repopulates them."""
        for label in SALESFORCE_SYNCED_MODELS:
            try:
                model = apps.get_model(label)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"  {label}: model not found, skipping"))
                continue
            count = model._base_manager.count()
            if count:
                model._base_manager.all().delete()
                self.stdout.write(f"  {label}: emptied {count} row(s)")
