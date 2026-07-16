import re

from django.db import migrations
from wagtail.blocks.stream_block import StreamValue

_HTML_TAG_RE = re.compile(r'<[a-zA-Z][^>]*>')


def _cell_at(row, index):
    cells = row.get('cells') or []
    return cells[index] if index < len(cells) else {'content': '', 'cta': []}


def _classify_column(rows, index):
    """A migrated column is 'cta' if any cell in it carries a CTA link,
    'rich_text' if any cell's content has HTML markup, else plain 'text'.
    Old sort-hint column types (number/date) are intentionally discarded —
    old cell content was always a free-text/rich-text string, never a real
    number or date, so there is nothing safe to parse into the new date/
    number cell types. Accepted limitation: a pre-existing number/date sort
    hint falls back to text sort after migration."""
    has_cta = False
    has_html = False
    for row in rows:
        cell = _cell_at(row, index)
        if cell.get('cta'):
            has_cta = True
        elif _HTML_TAG_RE.search(cell.get('content') or ''):
            has_html = True
    if has_cta:
        return 'cta'
    if has_html:
        return 'rich_text'
    return 'text'


def _cell_value(cell, column_type):
    if column_type == 'cta':
        return cell.get('cta') or []
    return cell.get('content') or ''


def _migrate_table_value(value):
    """Mutates a single 'table' block's raw `value` dict in place, replacing
    the old columns/rows ListBlock shape with the new manual TypedTableBlock
    shape. Returns True if anything changed. No-ops for tables that already
    have a data_source (dynamic tables store empty columns/rows anyway)."""
    if value.get('data_source'):
        return False
    columns = value.get('columns')
    rows = value.get('rows')
    if columns is None or rows is None:
        return False
    types = [_classify_column(rows, i) for i in range(len(columns))]
    value['manual'] = {
        'columns': [
            {'type': t, 'heading': col.get('header', '')}
            for t, col in zip(types, columns)
        ],
        'rows': [
            {'values': [_cell_value(_cell_at(row, i), types[i]) for i in range(len(columns))]}
            for row in rows
        ],
        'caption': '',
    }
    del value['columns']
    del value['rows']
    return True


def _fix_stream(node):
    """Walk StreamField raw data recursively and migrate every 'table' block
    found, however deeply nested (section/tabbed_content/etc). Mirrors the
    walk in 0187_cards_colors_csv_to_per_card.py."""
    changed = False
    if isinstance(node, list):
        for item in node:
            changed = _fix_stream(item) or changed
    elif isinstance(node, dict):
        if node.get('type') == 'table' and isinstance(node.get('value'), dict):
            changed = _migrate_table_value(node['value']) or changed
        for value in node.values():
            changed = _fix_stream(value) or changed
    return changed


def migrate_table_manual_rows(apps, schema_editor):
    RootPage = apps.get_model('pages', 'RootPage')
    for page in RootPage.objects.all().iterator():
        raw = list(page.body.raw_data)
        if _fix_stream(raw):
            page.body = StreamValue(page.body.stream_block, raw, is_lazy=True)
            page.save(update_fields=['body'])


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0199_alter_assignable_faqs_alter_faq_questions_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_table_manual_rows, migrations.RunPython.noop),
    ]
