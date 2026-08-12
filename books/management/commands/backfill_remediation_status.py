"""
Backfill Book/BookFacultyResources/BookStudentResources.remediation_status from
the hand-maintained accessibility remediation table on the Accessibility Hub
FlexPage (an `os-rem`-classed HTML table living in an `html` body block).

DRY RUN BY DEFAULT — pass --commit to write. Never creates records, only
updates existing Book/resource rows it can identify unambiguously. Rows it
can't confidently resolve (unknown book, no matching resource, ambiguous
resource name, corrupt column-shifted data, or a pre-existing differing
value without --overwrite) are written to a CSV report instead of guessed at.

Idempotent: re-running with the same source HTML and flags produces the same
end state (already-correct rows are left alone).
"""
import csv
import re
from itertools import groupby

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError

from books.models import Book

# Badge text -> field value, keyed by the same normalize() used for ancillary
# matching so lookups are consistent everywhere.
_STATUS_LABELS = {
    'Fixed': 'fixed',
    'In Progress': 'in_progress',
    'Deprecated': 'deprecated',
    'Removed': 'removed',
    'N/A': 'na',
}

# Resource Type values that narrow (or don't narrow) the resource search.
# Anything not in this set is itself an ancillary name that leaked into the
# type column (a handful of known one-offs) — treated as "search both" plus
# an extra match candidate.
_FACULTY_TYPES = {'instructor'}
_STUDENT_TYPES = {'student'}
_VIDEO_TYPES = {'videos'}
_KNOWN_TYPES = {'instructor', 'student', 'book', 'videos', 'instructor and student'}

REPORT_FIELDNAMES = ['subject', 'book_title', 'book_slug', 'resource_type', 'ancillary', 'status', 'reason']


def normalize(text):
    """casefold, strip punctuation/apostrophes, collapse internal whitespace."""
    text = (text or '').strip().casefold()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


STATUS_MAP = {normalize(label): value for label, value in _STATUS_LABELS.items()}


def slug_from_href(href):
    """Pull the book slug out of an /details/books/<slug> URL. None if unusable."""
    if not href:
        return None
    match = re.search(r'/details/books/([^/?#]+)', href)
    return match.group(1) if match else None


def _clean_text(tag):
    return ' '.join(tag.get_text(separator=' ').split())


def parse_table(html):
    """Parse the os-rem table into a flat, ordered list of row dicts:
    subject, book_title, book_href, book_slug, resource_type, ancillary,
    status_text, status_value (None if the badge text is unrecognized).
    """
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(class_='os-rem')
    if table is None:
        return []

    rows = []
    subject = book_title = book_href = book_slug = None

    for tr in table.find_all('tr'):
        classes = tr.get('class') or []
        if 'os-subj-row' in classes:
            subject = _clean_text(tr)
            continue
        if 'os-book-row' in classes:
            a = tr.find('a')
            if a is not None:
                book_href = a.get('href')
                book_title = _clean_text(a)
            else:
                book_href, book_title = None, _clean_text(tr)
            book_slug = slug_from_href(book_href)
            continue

        tds = tr.find_all('td')
        if len(tds) < 3:
            continue
        span = tds[2].find('span')
        status_text = (span.get_text(strip=True) if span is not None else tds[2].get_text(strip=True))
        rows.append({
            'subject': subject,
            'book_title': book_title,
            'book_href': book_href,
            'book_slug': book_slug,
            'resource_type': _clean_text(tds[0]),
            'ancillary': _clean_text(tds[1]),
            'status_text': status_text,
            'status_value': STATUS_MAP.get(normalize(status_text)),
        })
    return rows


def resolve_book(href, slug, title):
    """Slug match wins whenever there's a usable href. Title fallback only
    applies when the row had no href at all. Returns (book_or_None, via_title_fallback)."""
    if href:
        return (Book.objects.filter(slug=slug).first() if slug else None), False
    if title:
        return Book.objects.filter(title__iexact=title).first(), True
    return None, False


def find_resource(faculty, student, video, resource_type, ancillary):
    """Match `ancillary` (falling back to `resource_type` when the type column
    holds an ancillary name instead of a real type) against resource.heading.
    Returns a resource instance, 'AMBIGUOUS', or None."""
    rt_norm = normalize(resource_type)
    if rt_norm in _FACULTY_TYPES:
        pool = list(faculty)
    elif rt_norm in _STUDENT_TYPES:
        pool = list(student)
    elif rt_norm in _VIDEO_TYPES:
        pool = list(video)
    else:
        pool = list(faculty) + list(student) + list(video)

    # Ancillary is the primary candidate; resource_type is only a candidate
    # name when it isn't itself one of the real type labels (the one-off rows
    # where the type column leaked an ancillary name, e.g. "OER Commons Hub
    # Resources").
    candidates = [c for c in (ancillary, resource_type if rt_norm not in _KNOWN_TYPES else None) if c]

    for candidate in candidates:
        cand_norm = normalize(candidate)
        if not cand_norm:
            continue
        # resource_heading, not resource.heading: video rows have no resource FK.
        matches = [r for r in pool if normalize(r.resource_heading) == cand_norm]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            return 'AMBIGUOUS'
    return None


class Command(BaseCommand):
    help = (
        "Backfill Book/BookFacultyResources/BookStudentResources.remediation_status "
        "from the Accessibility Hub's hand-maintained os-rem HTML table. "
        "DRY RUN BY DEFAULT — pass --commit to write."
    )

    def add_arguments(self, parser):
        parser.add_argument('--page', type=int, default=None,
                             help="FlexPage id holding the os-rem table. Default: look up slug 'accessibility-hub'.")
        parser.add_argument('--html', default=None,
                             help="Parse a saved HTML file instead of a live page (e.g. an export).")
        parser.add_argument('--commit', action='store_true',
                             help="Write changes. Without this, runs in dry-run mode.")
        parser.add_argument('--overwrite', action='store_true',
                             help="Also overwrite fields that already hold a different, non-blank status.")
        parser.add_argument('--report', default='unmatched_remediation.csv',
                             help="Path to write the unmatched-rows CSV report.")

    def _load_html(self, options):
        if options['html']:
            with open(options['html'], encoding='utf-8') as f:
                return f.read()

        from pages.models import FlexPage
        if options['page'] is not None:
            try:
                page = FlexPage.objects.get(pk=options['page'])
            except FlexPage.DoesNotExist:
                raise CommandError(f"No FlexPage with id {options['page']}.")
        else:
            page = FlexPage.objects.filter(slug='accessibility-hub').first()
            if page is None:
                raise CommandError(
                    "No FlexPage found with slug 'accessibility-hub'. Pass --page <id> or --html <path>.")

        for block in page.body:
            if block.block_type == 'html' and 'os-rem' in str(block.value):
                return str(block.value)
        raise CommandError(f"FlexPage {page.pk} ('{page.slug}') has no 'os-rem' HTML table block in its body.")

    def handle(self, *args, **options):
        commit = options['commit']
        overwrite = options['overwrite']

        if not commit:
            self.stdout.write(self.style.WARNING(
                "*** DRY RUN — no changes will be written. Pass --commit to save. ***"))

        html = self._load_html(options)
        rows = parse_table(html)
        if not rows:
            raise CommandError("Parsed 0 rows from the os-rem table — check the source.")

        report_rows = []
        matched = unmatched = already_correct = already_different = 0
        applied = {}
        title_fallback_books = []
        pending_writes = []  # (instance, new_status)

        def report(row, reason):
            report_rows.append({
                'subject': row.get('subject') or '',
                'book_title': row.get('book_title') or '',
                'book_slug': row.get('book_slug') or '',
                'resource_type': row.get('resource_type', ''),
                'ancillary': row.get('ancillary', ''),
                'status': row.get('status_value') or row.get('status_text') or '',
                'reason': reason,
            })

        book_groups = groupby(rows, key=lambda r: (r['book_href'], r['book_title']))
        for _key, group_iter in book_groups:
            group = list(group_iter)
            first = group[0]
            book, via_title = resolve_book(first['book_href'], first['book_slug'], first['book_title'])

            if book is None:
                unmatched += len(group)
                report(first, f'book_not_found ({len(group)} rows affected)')
                continue
            if via_title:
                title_fallback_books.append((first['book_title'], book.slug))

            # resource is SET_NULL, so a deleted snippet leaves rows whose
            # resource_heading property raises. They can't match a heading anyway.
            faculty = list(book.book_faculty_resources.exclude(resource__isnull=True))
            student = list(book.book_student_resources.exclude(resource__isnull=True))
            video = list(book.book_video_faculty_resources.all())

            for row in group:
                status_value = row['status_value']
                ancillary, resource_type = row['ancillary'], row['resource_type']

                if status_value is None:
                    unmatched += 1
                    report(row, 'unrecognized_status')
                    continue

                # Column-shifted corruption: the ancillary cell holds a status
                # badge's text instead of a real ancillary name. Don't guess.
                if normalize(ancillary) in STATUS_MAP:
                    unmatched += 1
                    report(row, 'column_shifted')
                    continue

                is_web_pdf = normalize(ancillary) == normalize('Web PDF') or normalize(resource_type) == 'book'
                if is_web_pdf:
                    target = book
                else:
                    target = find_resource(faculty, student, video, resource_type, ancillary)

                if target is None:
                    unmatched += 1
                    report(row, 'no_resource')
                    continue
                if target == 'AMBIGUOUS':
                    unmatched += 1
                    report(row, 'ambiguous')
                    continue

                matched += 1
                current = target.remediation_status or ''
                if current == status_value:
                    already_correct += 1
                    continue
                if current:
                    already_different += 1
                    report(row, f'existing_value_differs (current={current!r})')
                    if not overwrite:
                        continue

                applied[status_value] = applied.get(status_value, 0) + 1
                pending_writes.append((type(target), target.pk, status_value))

        if commit:
            # Direct column update, not instance.save(): Book.save() propagates
            # several fields to every other Book in its locale and Page.save()
            # runs full_clean() by default — neither is wanted (or safe) when
            # bulk-touching 75+ books, and convert_book_images.py already
            # establishes this pattern for Book in this same app.
            for model_cls, pk, status_value in pending_writes:
                model_cls.objects.filter(pk=pk).update(remediation_status=status_value)

        report_path = options['report']
        with open(report_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=REPORT_FIELDNAMES)
            writer.writeheader()
            writer.writerows(report_rows)

        self.stdout.write(
            f"Parsed {len(rows)} rows. matched={matched} unmatched={unmatched} "
            f"already_correct={already_correct} already_different={already_different} "
            f"({'overwritten' if overwrite else 'not overwritten'})")
        applied_summary = ', '.join(f'{k}={v}' for k, v in sorted(applied.items())) or 'none'
        self.stdout.write(f"{'Applied' if commit else 'Would apply'}: {applied_summary}")
        self.stdout.write(f"Unmatched-row report written to {report_path} ({len(report_rows)} rows).")
        if title_fallback_books:
            self.stdout.write(self.style.WARNING(
                f"{len(title_fallback_books)} book(s) matched by title fallback (no usable href) — verify these:"))
            for title, slug in title_fallback_books:
                self.stdout.write(f"  {title!r} -> slug={slug!r}")
        if not commit:
            self.stdout.write(self.style.WARNING(
                "*** DRY RUN — no changes were written. Pass --commit to save. ***"))
