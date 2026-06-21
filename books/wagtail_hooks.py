from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.views.pages.listing import IndexView
from wagtail.admin.viewsets.pages import PageListingViewSet

from books.models import Book


class BookListingIndexView(IndexView):
    default_ordering = "title"


class BookPageListingViewSet(PageListingViewSet):
    """A top-level, filterable listing of Book *detail pages*.

    Book detail pages live in the page tree (under a BookIndex), so this is a
    listing/shortcut into the explorer rather than a separate store — editing a
    book from here opens the normal page editor."""

    model = Book
    index_view_class = BookListingIndexView
    icon = "doc-full"
    menu_label = "Books"
    menu_name = "books"
    menu_order = 205
    add_to_admin_menu = False


@hooks.register("register_admin_viewset")
def register_book_listing_viewset():
    return BookPageListingViewSet("books")


@hooks.register("register_content_menu_item")
def register_books_content_menu_item():
    return MenuItem(
        "Books",
        reverse("books:index"),
        name="books",
        icon_name="doc-full",
        order=100,
    )
