from django.db import migrations


# The `component_key` and `region` columns were added to oxmenus_menus by an
# older PR (core-oxmenu-nav-regions) that was thrown away before merging. The
# columns are NOT NULL with no DB default, so they were left orphaned on the
# dev database and reject every insert from the current (column-less) model.
# Drop them. IF EXISTS keeps this a no-op on databases that never received
# those columns (fresh installs, CI, prod).
DROP_ORPHAN_COLUMNS = """
ALTER TABLE oxmenus_menus DROP COLUMN IF EXISTS component_key;
ALTER TABLE oxmenus_menus DROP COLUMN IF EXISTS region;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("oxmenus", "0005_alter_menus_options_menus_sort_order_and_more"),
    ]

    operations = [
        migrations.RunSQL(DROP_ORPHAN_COLUMNS, reverse_sql=migrations.RunSQL.noop),
    ]
