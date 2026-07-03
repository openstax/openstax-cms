from django.db import migrations
from wagtail.blocks.stream_block import StreamValue


def _split_colors(value):
    """Turn a stored comma-separated hex string into a list of colors."""
    if not isinstance(value, str):
        return []
    return [c.strip() for c in value.split(',') if c.strip()]


def _fix_stream(node):
    """Walk StreamField raw data and rewrite every cards_block: move the
    block-level accent_colors / divider_colors config (comma-separated,
    cycled per card) onto the cards themselves as accent_color /
    divider_color, cycling the same way the renderer did. Recurses so cards
    blocks nested in sections/wells/columns are covered. Returns True if
    anything changed."""
    changed = False
    if isinstance(node, list):
        for item in node:
            changed = _fix_stream(item) or changed
    elif isinstance(node, dict):
        if node.get('type') == 'cards_block' and isinstance(node.get('value'), dict):
            value = node['value']
            config = value.get('config', []) or []
            accents = []
            dividers = []
            remaining = []
            for cfg in config:
                if isinstance(cfg, dict) and cfg.get('type') == 'accent_colors':
                    accents = _split_colors(cfg.get('value'))
                elif isinstance(cfg, dict) and cfg.get('type') == 'divider_colors':
                    dividers = _split_colors(cfg.get('value'))
                else:
                    remaining.append(cfg)
                    continue
                changed = True
            if len(remaining) != len(config):
                value['config'] = remaining
            if accents or dividers:
                for i, card in enumerate(value.get('cards', []) or []):
                    card_value = card.get('value') if isinstance(card.get('value'), dict) else card
                    if not isinstance(card_value, dict):
                        continue
                    if accents:
                        card_value['accent_color'] = accents[i % len(accents)]
                    if dividers:
                        card_value['divider_color'] = dividers[i % len(dividers)]
        for value in node.values():
            changed = _fix_stream(value) or changed
    return changed


def csv_colors_to_per_card(apps, schema_editor):
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
        ('pages', '0186_alter_rootpage_body'),
    ]

    operations = [
        migrations.RunPython(csv_colors_to_per_card, migrations.RunPython.noop),
    ]
