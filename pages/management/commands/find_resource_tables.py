from django.core.management.base import BaseCommand

from pages.models import RootPage


def _find_tables(node, path=''):
    if isinstance(node, list):
        for i, item in enumerate(node):
            yield from _find_tables(item, f'{path}[{i}]')
    elif isinstance(node, dict):
        if node.get('type') == 'table' and isinstance(node.get('value'), dict):
            yield path, node['value']
        for key, value in node.items():
            yield from _find_tables(value, f'{path}.{key}')


def _looks_like_book_resources(table_value):
    if table_value.get('data_source'):
        return False
    columns = (table_value.get('manual') or {}).get('columns') or []
    cta_columns = [c for c in columns if c.get('type') == 'cta']
    book_columns = [c for c in columns if 'book' in (c.get('heading') or '').lower()]
    return len(cta_columns) == 1 and len(book_columns) >= 1


class Command(BaseCommand):
    help = ('Find manual tables that duplicate what the book_resources dynamic '
            'source already generates (one CTA column + a "Book(s)"-style column). '
            'Dry-run only: reports candidates for manual review, does not rewrite anything.')

    def handle(self, *args, **options):
        found = 0
        for page in RootPage.objects.live().specific().iterator():
            try:
                tables = list(_find_tables(list(page.body.raw_data)))
            except Exception as e:
                # This command scans broad, less-trusted content across every
                # live page — one malformed body shouldn't kill the report
                # for every other page. (The data migration in Task 3
                # deliberately does NOT do this: it touches only our own
                # known table-block shape, so a malformed block there is a
                # real anomaly that should surface loudly, not be skipped.)
                self.stderr.write(f'Skipping page {page.id} "{page.title}": {e}')
                continue
            for path, table_value in tables:
                if not _looks_like_book_resources(table_value):
                    continue
                found += 1
                manual = table_value.get('manual') or {}
                headers = [c.get('heading') for c in manual.get('columns') or []]
                sample = (manual.get('rows') or [])[:1]
                self.stdout.write(
                    f'Page {page.id} "{page.title}" — table at body{path}\n'
                    f'  columns: {headers}\n'
                    f'  sample row: {sample}\n'
                    f'  edit: /admin/pages/{page.id}/edit/\n'
                )
        if not found:
            self.stdout.write('No candidate tables found.')
