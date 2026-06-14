from wagtail import hooks
from wagtail.admin.viewsets.pages import PageListingViewSet

from books.models import Book


class BookPageListingViewSet(PageListingViewSet):
    """A top-level, filterable listing of Book *detail pages*.

    Book detail pages live in the page tree (under a BookIndex), so this is a
    listing/shortcut into the explorer rather than a separate store — editing a
    book from here opens the normal page editor. Placed right after "Subjects"
    in the sidebar (menu_order 205 vs Subjects' 200)."""

    model = Book
    icon = "doc-full"
    menu_label = "Books"
    menu_name = "books"
    menu_order = 205
    add_to_admin_menu = True


@hooks.register("register_admin_viewset")
def register_book_listing_viewset():
    return BookPageListingViewSet("books")
