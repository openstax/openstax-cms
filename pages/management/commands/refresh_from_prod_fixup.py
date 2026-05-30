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

Dry-run by default. Refuses to run when ENVIRONMENT == 'prod'.

Idempotent: the URL patterns include a scheme or `//` prefix so a second
run does not double-rewrite (`https://dev.openstax.org` does not contain
the substring `https://openstax.org`).
"""
import json

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page, Site


DEFAULT_SOURCE_HOST = 'openstax.org'

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
        self.stdout.write(
            f"{mode} replacing {source_host} → {target_host}"
        )

        replacements = _replacements(source_host, target_host)

        with transaction.atomic():
            self._update_site(target_host)
            self._rewrite_concrete_models(replacements)
            self._rewrite_page_revisions(replacements)
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
        site.hostname = target_host
        site.save()
        self.stdout.write(f"  Site.hostname: {old} → {target_host}")

    def _rewrite_concrete_models(self, replacements):
        """Walk all concrete project models, rewriting URL-bearing field values."""
        url_field_types = (RichTextField, StreamField, models.URLField)

        for model in apps.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            if model._meta.app_label in SKIP_APP_LABELS:
                continue

            # Bucket fields: specialized URL fields vs plain text/char that MIGHT carry URLs.
            url_fields, text_fields = [], []
            for field in model._meta.fields:
                if isinstance(field, url_field_types):
                    url_fields.append(field)
                elif isinstance(field, (models.TextField, models.CharField)):
                    text_fields.append(field)

            if not url_fields and not text_fields:
                continue

            changed_rows = 0
            for instance in model.objects.all().iterator():
                row_changed = False
                for field in url_fields:
                    if self._rewrite_field_on_instance(instance, field, replacements):
                        row_changed = True
                for field in text_fields:
                    if self._rewrite_field_on_instance(instance, field, replacements):
                        row_changed = True
                if row_changed:
                    instance.save()
                    changed_rows += 1
            if changed_rows:
                self.stdout.write(f"  {model._meta.label}: rewrote {changed_rows} row(s)")

    def _rewrite_field_on_instance(self, instance, field, replacements):
        """Rewrite one field's value in place on an instance. Returns whether it changed."""
        value = getattr(instance, field.name)
        if value is None:
            return False

        if isinstance(field, StreamField):
            # StreamField stored as JSON text in DB; rewrite at the JSON level so any
            # block type with URLs inside it gets covered without per-block knowledge.
            try:
                raw = value.raw_data if hasattr(value, 'raw_data') else json.loads(str(value))
            except (TypeError, ValueError):
                return False
            json_str = json.dumps(raw)
            new_json, changed = _apply(json_str, replacements)
            if changed:
                setattr(instance, field.name, json.loads(new_json))
            return changed

        if isinstance(value, str):
            new_value, changed = _apply(value, replacements)
            if changed:
                setattr(instance, field.name, new_value)
            return changed

        return False

    def _truncate_salesforce_synced_data(self):
        """Empty Salesforce-synced data tables so the next sync repopulates them."""
        for label in SALESFORCE_SYNCED_MODELS:
            try:
                model = apps.get_model(label)
            except LookupError:
                self.stdout.write(self.style.WARNING(f"  {label}: model not found, skipping"))
                continue
            count = model.objects.count()
            if count:
                model.objects.all().delete()
                self.stdout.write(f"  {label}: emptied {count} row(s)")

    def _rewrite_page_revisions(self, replacements):
        """Rewrite the latest revision per page so the admin editor reflects new URLs."""
        count = 0
        for page in Page.objects.all().iterator():
            rev = page.get_latest_revision()
            if rev is None:
                continue
            try:
                content = rev.content
            except AttributeError:
                continue
            if not content:
                continue
            json_str = json.dumps(content)
            new_json, changed = _apply(json_str, replacements)
            if changed:
                rev.content = json.loads(new_json)
                rev.save(update_fields=['content'])
                count += 1
        if count:
            self.stdout.write(f"  wagtailcore.Revision: rewrote {count} latest revision(s)")
