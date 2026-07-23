import uuid

from django.db import migrations
from wagtail.blocks.stream_block import StreamValue


def _fix_stream(node):
    """Walk StreamField raw data and rewrite every cards_block: move each
    card's flat accent_color / divider_color fields into the card's nested
    config StreamBlock. Recurses so cards blocks nested in sections/wells/
    columns are covered. Returns True if anything changed."""
    changed = False
    if isinstance(node, list):
        for item in node:
            changed = _fix_stream(item) or changed
    elif isinstance(node, dict):
        if node.get('type') == 'cards_block' and isinstance(node.get('value'), dict):
            value = node['value']
            for card in value.get('cards', []) or []:
                card_value = card.get('value') if isinstance(card.get('value'), dict) else card
                if not isinstance(card_value, dict):
                    continue
                for field in ('accent_color', 'divider_color'):
                    color = card_value.pop(field, None)
                    if color:
                        config = card_value.setdefault('config', [])
                        config.append({
                            'type': field,
                            'id': str(uuid.uuid4()),
                            'value': color,
                        })
                        changed = True
        for value in node.values():
            changed = _fix_stream(value) or changed
    return changed


def flat_colors_to_config(apps, schema_editor):
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
            # without re-validating against the changed block def.
            page.body = StreamValue(page.body.stream_block, raw, is_lazy=True)
            page.save(update_fields=['body'])


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0200_alter_rootpage_body'),
    ]

    operations = [
        migrations.RunPython(flat_colors_to_config, migrations.RunPython.noop),
    ]
