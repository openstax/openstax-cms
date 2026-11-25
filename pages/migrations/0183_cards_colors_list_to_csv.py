from django.db import migrations
from wagtail.blocks.stream_block import StreamValue


def _join_colors(value):
    """Turn a stored ListBlock value (a list of hex strings, each possibly
    wrapped in a {'type','id','value'} item dict) into a comma-separated
    string. Anything already a string is returned untouched."""
    if not isinstance(value, list):
        return value
    parts = []
    for item in value:
        color = item.get('value', '') if isinstance(item, dict) else item
        color = str(color).strip()
        if color:
            parts.append(color)
    return ','.join(parts)


def _fix_stream(node):
    """Walk StreamField raw data and rewrite every cards_block's accent_colors
    / divider_colors from a list of hex strings to a single comma-separated
    string. Recurses so cards blocks nested in sections/wells/columns are
    covered. Returns True if anything changed."""
    changed = False
    if isinstance(node, list):
        for item in node:
            changed = _fix_stream(item) or changed
    elif isinstance(node, dict):
        if node.get('type') == 'cards_block' and isinstance(node.get('value'), dict):
            for cfg in node['value'].get('config', []) or []:
                if (isinstance(cfg, dict)
                        and cfg.get('type') in ('accent_colors', 'divider_colors')
                        and isinstance(cfg.get('value'), list)):
                    cfg['value'] = _join_colors(cfg['value'])
                    changed = True
        for value in node.values():
            changed = _fix_stream(value) or changed
    return changed


def list_colors_to_csv(apps, schema_editor):
    # RootPage is concrete and FlexPage inherits it, so iterating RootPage
    # covers the body of both. Migrates live/draft body only; old revisions are
    # not rewritten (these configs are new, so there is little revision history).
    RootPage = apps.get_model('pages', 'RootPage')
    for page in RootPage.objects.all().iterator():
        # raw_data is a RawDataView wrapper, not a plain list; materialize it so
        # the recursion below sees real lists/dicts and mutates them in place.
        raw = list(page.body.raw_data)
        if _fix_stream(raw):
            # A lazy StreamValue serializes raw_data straight back to the column
            # without re-validating against the (now comma-separated) block def.
            page.body = StreamValue(page.body.stream_block, raw, is_lazy=True)
            page.save(update_fields=['body'])


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0182_alter_rootpage_body'),
    ]

    operations = [
        migrations.RunPython(list_colors_to_csv, migrations.RunPython.noop),
    ]
