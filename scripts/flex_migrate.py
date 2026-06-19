#!/usr/bin/env python3
"""Move one FlexPage's live content between OpenStax CMS environments over HTTP.

Exports the page's live, sanitized layout/body from the source env and imports it
as an unpublished draft on the target env. You then re-add images/links and publish
in the Wagtail admin. Requires a staff API token on each environment.

Example:
    python scripts/flex_migrate.py --page-id 568 --parent-id 30 \
      --source https://dev.openstax.org/apps/cms/api/v2/pages/flex --source-token "$DEV_TOKEN" \
      --target https://staging.openstax.org/apps/cms/api/v2/pages/flex --target-token "$STG_TOKEN"
"""
import argparse
import sys


def assemble_import_body(export_json, parent_id):
    return {**export_json, "parent_id": parent_id}


def run_migration(*, source_base, source_token, target_base, target_token,
                  page_id, parent_id, http_get, http_post):
    src = source_base.rstrip("/")
    tgt = target_base.rstrip("/")
    get_resp = http_get(f"{src}/{page_id}/export/",
                        headers={"Authorization": f"Token {source_token}"})
    get_resp.raise_for_status()
    body = assemble_import_body(get_resp.json(), parent_id)
    post_resp = http_post(f"{tgt}/import/", json=body,
                          headers={"Authorization": f"Token {target_token}"})
    post_resp.raise_for_status()
    return post_resp.json()


def main(argv=None):
    p = argparse.ArgumentParser(description="Migrate a FlexPage between CMS environments.")
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--parent-id", type=int, required=True, help="Parent page id on the TARGET env.")
    p.add_argument("--source", required=True, help="Source flex API base URL.")
    p.add_argument("--source-token", required=True)
    p.add_argument("--target", required=True, help="Target flex API base URL.")
    p.add_argument("--target-token", required=True)
    args = p.parse_args(argv)

    import requests  # imported here so the testable helpers need no network dep
    try:
        result = run_migration(
            source_base=args.source, source_token=args.source_token,
            target_base=args.target, target_token=args.target_token,
            page_id=args.page_id, parent_id=args.parent_id,
            http_get=requests.get, http_post=requests.post,
        )
    except requests.HTTPError as exc:
        resp = exc.response
        print(f"HTTP {resp.status_code} from {resp.url}\n{resp.text}", file=sys.stderr)
        return 1
    print(f"Imported as draft id={result['id']} (live={result['live']}).")
    print(f"Open and publish: {result.get('edit_url', '(see admin)')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
