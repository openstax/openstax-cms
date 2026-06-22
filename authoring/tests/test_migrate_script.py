# authoring/tests/test_migrate_script.py
import importlib.util
import os
from django.test import TestCase

_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "scripts", "flex_migrate.py",
)


def _load():
    spec = importlib.util.spec_from_file_location("flex_migrate", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class MigrateScriptTests(TestCase):
    def test_assemble_import_body_injects_parent(self):
        m = _load()
        body = m.assemble_import_body({"title": "T", "slug": "s", "layout": [], "body": []}, 30)
        self.assertEqual(body["parent_id"], 30)
        self.assertEqual(body["title"], "T")

    def test_run_migration_calls_export_then_import(self):
        m = _load()
        calls = {}

        class Resp:
            status_code = 200
            def __init__(self, data): self._data = data
            def json(self): return self._data
            def raise_for_status(self): pass

        def fake_get(url, headers=None):
            calls["get_url"] = url
            return Resp({"title": "T", "slug": "s", "layout": [], "body": []})

        def fake_post(url, json=None, headers=None):
            calls["post_url"] = url
            calls["post_body"] = json
            return Resp({"id": 123, "live": False, "edit_url": "/admin/pages/123/edit/"})

        out = m.run_migration(
            source_base="https://dev/x", source_token="D",
            target_base="https://stg/x", target_token="S",
            page_id=568, parent_id=30, http_get=fake_get, http_post=fake_post,
        )
        self.assertEqual(calls["get_url"], "https://dev/x/568/export/")
        self.assertEqual(calls["post_url"], "https://stg/x/import/")
        self.assertEqual(calls["post_body"]["parent_id"], 30)
        self.assertEqual(out["id"], 123)
