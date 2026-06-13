# Refreshing a Non-Prod Environment from Prod

This is the operational runbook for rebuilding dev or staging from a prod
snapshot. It's the "Option 1" path described in
[`wagtail-transfer-page-sync.md`](./wagtail-transfer-page-sync.md) — it brings
the target environment to identical data with prod, then aligns the
`wagtail_transfer_idmapping` UUIDs so future page transfers from prod work as
updates rather than creating duplicates.

After completing this runbook on a target env, that env will be data-identical
to prod (with URLs rewritten to match the target host), and wagtail-transfer
will be able to keep it in sync with prod going forward. The CMS `auth_user`
table contains only internal OpenStax staff accounts, so user data is carried
across intentionally — this means engineers can log into dev/staging with
their prod credentials after the refresh.

> **This procedure is destructive on the target environment.** Every existing
> row in the target DB and every file in the target S3 bucket will be
> overwritten. Make sure no editors are mid-edit on the target before
> starting.

## When to do this

- First time setting up wagtail-transfer across envs.
- Periodic refresh (we suggested quarterly in the page-sync doc) so dev and
  staging don't drift indefinitely from prod.
- Recovery after a major content incident on a non-prod env.

**Never run this against prod.** The fixup management command has a guard
that refuses to run when `ENVIRONMENT == 'prod'`, but you should also refuse
mentally — pg_dump and `aws s3 sync` don't have that guard.

## Prerequisites

Before you start, confirm:

- [ ] **Access to prod DB** — credentials/SSH that let you run `pg_dump`
      against the prod Postgres instance.
- [ ] **Access to target env DB** — credentials that let you drop/recreate
      tables in dev or staging Postgres.
- [ ] **AWS credentials** with read on the prod media bucket and
      read/write on the target env's media bucket. Cross-account access may
      require a profile that can assume into both accounts.
- [ ] **The target environment is freezing writes.** Tell editors that
      anything they edit on dev/staging right now will be lost. Pause cron
      jobs / scheduled tasks on the target env.
- [ ] **Disk space** — Postgres dump for the prod CMS is on the order of
      a few hundred MB to a few GB depending on revisions history. Wherever
      you stage the dump file needs the room.
- [ ] **The PR with `wagtail-transfer` is deployed to all three envs.**
      Specifically: the `wagtail_transfer_idmapping` table must exist on
      both prod (source of preseed) and the target env (where we restore).
- [ ] **Snippet uniqueness migration applied cleanly.** That PR adds
      per-locale `UniqueConstraint`s to the snippets used as transfer lookup
      keys (so imports match instead of duplicating). `AddConstraint` *fails*
      if existing data already violates a constraint — e.g. two same-name
      `Subject`s in one locale, or more than one of a singleton snippet
      (`NoWebinarMessage`, `AmazonBookBlurb`, `ContentWarning`,
      `RequireLoginMessage`) per locale. If the migration errored on deploy,
      dedupe the offending rows on that env, then re-run `migrate` before
      proceeding.

## Step 1 — Preseed prod's IDMapping table

This is the step that makes everything else worth doing. It assigns
deterministic UUIDs to every page, image, document, and auth user on prod,
storing them in `wagtail_transfer_idmapping`. When we dump and restore that
table onto the target env in step 3, the target env ends up with the same
UUIDs prod has, which is what lets wagtail-transfer recognize "the same
page" between the two.

```bash
# on a prod app instance
./manage.py preseed_transfer_table auth wagtailcore wagtailimages.image wagtaildocs
```

This is **idempotent** — running it twice just no-ops on already-mapped
rows. Safe to re-run if interrupted.

## Step 2 — Dump prod's database

From a machine with prod DB access (an app instance, a bastion, wherever
your team typically does this):

```bash
pg_dump \
  --no-owner --no-privileges \
  --exclude-table=django_session \
  --exclude-table-data='django_admin_log' \
  --format=custom \
  --file=/tmp/oscms_prod_$(date +%Y%m%d).dump \
  $PROD_DATABASE_URL
```

Notes on what's excluded:
- **`django_session`** — session cookies. Useless on a different host, and
  bloats the dump. Editors will need to re-login on the target env.
- **`django_admin_log`** — Django admin history. Not worth carrying over.

Move the dump to wherever you'll restore from (laptop, target instance, S3
staging bucket, etc.). It contains live prod data; treat it as sensitive
and delete it when you're done.

## Step 3 — Restore onto the target environment

> Skip ahead and run `./manage.py migrate` afterward if your prod and target
> branches happen to be at different migration revisions. Otherwise the
> restored schema may be ahead of the running app's models.

```bash
# on the target env (dev or staging), against its DB:

# Drop and recreate so we get a clean slate
dropdb $TARGET_DATABASE_NAME
createdb $TARGET_DATABASE_NAME

# Restore from the dump
pg_restore \
  --no-owner --no-privileges \
  --dbname=$TARGET_DATABASE_NAME \
  /tmp/oscms_prod_YYYYMMDD.dump

# Sanity check the sequences match the max IDs
psql $TARGET_DATABASE_URL -c "SELECT setval(pg_get_serial_sequence('wagtailcore_page', 'id'), MAX(id)) FROM wagtailcore_page;"
```

(That last `setval` is belt-and-suspenders — pg_dump usually handles
sequences correctly with the `custom` format, but it's been known to drift.
Repeat for any table you've seen `IntegrityError: duplicate key` on after a
prior restore.)

## Step 4 — Sync the S3 media bucket

Prod media (uploaded images, documents) lives in prod's S3 bucket. The DB
you just restored references those files by path; if the target env's
bucket doesn't have them, every image in the admin shows broken.

```bash
# Read-only sweep — see what would change before doing it
aws s3 sync \
  s3://$PROD_MEDIA_BUCKET/ \
  s3://$TARGET_MEDIA_BUCKET/ \
  --dryrun --delete

# When the dry run looks right
aws s3 sync \
  s3://$PROD_MEDIA_BUCKET/ \
  s3://$TARGET_MEDIA_BUCKET/ \
  --delete
```

Notes:
- `--delete` removes files from the target bucket that don't exist in prod.
  That's what you want — anything uploaded to dev/staging that's not on
  prod is about to be orphaned anyway when the DB no longer references it.
- If your buckets live in different AWS accounts, you'll need a profile
  that can read from one and write to the other, or copy via an
  intermediate bucket. Your AWS setup will dictate which.
- If your team uses bucket-level encryption keys (SSE-KMS), the copying
  identity also needs `kms:Decrypt` on the source key and `kms:Encrypt`
  on the destination key.

## Step 5 — Run the fixup management command

This is the part you don't want to forget. After step 3, the target env's
DB believes it *is* prod — Wagtail Site is `openstax.org`, all the URLs in
StreamField/RichText content reference `openstax.org`, and `auth_user`
contains real prod users.

The command writes exclusively with set-based `UPDATE`s (`queryset.update()`),
never `model.save()`. That is deliberate: it means the rewrite never fires
`post_save` signals or model `save()` overrides, so running it against a
freshly restored prod dataset will **not** email real errata submitters,
issue CloudFront invalidations against prod's distribution, or call out to
Salesforce — all of which would otherwise happen once per touched row. The
trade-off is that it also does not re-index search; rebuild the index
afterward if you use a non-database backend (see Common pitfalls #4).

```bash
# on the target env

# 1. Dry-run first. Read the output and confirm what it says it'll change.
./manage.py refresh_from_prod_fixup --target-host=dev.openstax.org

# 2. Commit it
./manage.py refresh_from_prod_fixup \
  --target-host=dev.openstax.org \
  --commit
```

Use the appropriate `--target-host` for the env you're refreshing:
- dev: `dev.openstax.org`
- staging: `staging.openstax.org`

User accounts come across with the dump/restore in step 3 and the fixup
command leaves them alone — the CMS `auth_user` table holds only internal
staff, so carrying it across means engineers can log into the refreshed
env with the same credentials they use on prod.

The fixup also **empties Salesforce-synced data tables** (`Adopter`,
`AdoptionOpportunityRecord`, `School`, `Partner`, `ResourceDownload`,
`SavingsNumber`). Prod salesforce IDs point at prod's Salesforce instance,
which isn't what dev/staging is configured to talk to — so the next
scheduled run of `update_partners`, `update_schools`, etc. will repopulate
those tables with the target env's sandbox data. Salesforce config tables
(`SalesforceSettings`, `SalesforceForms`, the `*Mapping` models) are left
intact.

> One thing to be aware of: any locally-uploaded media on Partner records
> (logos, images, videos) is referenced by row, so emptying the table
> orphans those files in S3 until the next Partner sync re-establishes
> the references. If a partner is missing imagery after the refresh, run
> `./manage.py update_partners` and confirm.

After this, restart the target env's web workers so any in-memory caches
clear.

## Step 6 — Verify

Sanity checks to run on the target env:

```bash
# Site hostname is right
psql $TARGET_DATABASE_URL -c "SELECT hostname FROM wagtailcore_site WHERE is_default_site;"

# No leftover prod URLs in obvious places
psql $TARGET_DATABASE_URL -c "SELECT COUNT(*) FROM snippets_givebanner WHERE link_url LIKE 'https://openstax.org%';"

# wagtail_transfer_idmapping is populated and traveled over from prod
psql $TARGET_DATABASE_URL -c "SELECT COUNT(*) FROM wagtail_transfer_idmapping;"
```

Then in the browser:
1. Log into the target env's admin as a superuser.
2. Open the home page in the page tree — pages from prod should be there.
3. Open a page that has hero images / StreamField content — confirm images
   render and that any URLs in the content show the target host, not
   `openstax.org`.
4. Open Wagtail's Import view (Settings → Import or wherever the menu item
   is) and pick prod as the source. Browse the page tree. Pick a page that
   has been edited on prod since the dump and import it — it should resolve
   as an **update** rather than create a duplicate, because the
   `wagtail_transfer_idmapping` UUIDs match.

If the last check creates a duplicate instead of updating, step 1 (preseed
on prod) didn't happen or didn't include `wagtailcore` — go back and check.

## Rollback / if it goes sideways

The pg_dump/restore step is the destructive one. If you realize mid-step
that you needed something from the target DB that's now gone:

- **Before step 3**: nothing's gone yet. You can stop without consequences.
- **After step 3, before step 5**: the target DB is now prod data. To
  restore the previous target state, you need a pre-refresh backup of that
  env. Take one *before* step 3 if there's anything on dev/staging worth
  keeping (in-progress edits, etc.).

For S3, `aws s3 sync --delete` removes target-only files. Same advice:
take a snapshot of the target bucket (or rely on bucket versioning if
enabled) before step 4 if you care about anything that lives only there.

## Common pitfalls

1. **Forgetting step 1 (preseed on prod).** If you skip preseed, the
   target env's `wagtail_transfer_idmapping` will be empty for pages
   created before this refresh. Future imports from prod will create
   duplicates instead of updating. Catch: import a test page after step 6
   and confirm it updates rather than duplicates.

2. **Schema drift between prod and target branches.** If prod is running
   migration `0099` and the target branch is at `0095`, the restored
   schema is ahead of the target's models. Symptoms: `manage.py migrate`
   tries to undo migrations, or admin views throw `ProgrammingError`.
   Resolution: get the target branch caught up to prod, OR cherry-pick the
   relevant migrations onto the target branch before refreshing.

3. **CloudFront / CDN caching.** The CDN may still be serving cached
   responses from before the refresh. Issue an invalidation
   (`/*` is the nuclear option; usually you only need a few paths) if
   pages look wrong immediately after refresh and look right after a few
   minutes.

4. **Wagtail search index out of sync.** If your search backend is
   Elasticsearch (rather than Postgres FTS), run
   `./manage.py update_index` after step 5.

5. **Cron jobs reactivating before you're ready.** Cron tasks that send
   emails, sync to Salesforce, or otherwise reach outside the app should
   stay paused until you've verified step 6. Otherwise you might email
   prod users from your dev environment, etc.

6. **Salesforce tables empty until the next sync.** The fixup empties
   the synced tables on purpose (see Step 5), so the admin will show
   "no partners," "no schools," etc. until the next scheduled sync runs.
   If that's blocking verification, run the sync commands manually:
   ```
   ./manage.py update_partners
   ./manage.py update_schools
   ./manage.py update_opportunities
   ./manage.py update_resource_downloads
   ```

## Reusing this for a new environment

If you ever stand up a new environment (e.g., a `qa` env), this same
procedure works. Steps:

1. Deploy the codebase to the new env.
2. Run `./manage.py migrate` so the schema is in place.
3. Add the new env's hostname and secret key to prod's
   `WAGTAILTRANSFER_SOURCES_JSON` if you want prod to be able to pull
   from it (usually you don't).
4. Run this runbook with `--target-host=qa.openstax.org`.

After that, the new env is ready for normal wagtail-transfer use.
