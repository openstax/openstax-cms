# pages/promote_home.py
"""Copy a FlexPage's content onto the environment's RootPage as a draft revision.

Mirrors the never-publish contract of authoring/drafts.py: this only ever
creates a draft Revision on the site's RootPage. A human reviews and publishes
in the Wagtail admin.
"""
from wagtail.models import Site

from pages.models import RootPage

PROMOTED_FIELDS = ('layout', 'body', 'school', 'promote_image', 'seo_title', 'search_description')


class PromoteError(Exception):
    """Base class for promote-to-home errors."""


class HomePageNotFound(PromoteError):
    """No default Site, no root page, or the root page isn't exactly a RootPage."""


class HomePageLocked(PromoteError):
    """The site root page is locked and can't be edited right now."""


class PromotePermissionDenied(PromoteError):
    """The user doesn't have edit permission on the site root page."""


def promote_to_home(flex_page, user):
    """Copy `flex_page`'s latest (possibly draft) content onto the default
    Site's RootPage as a new draft revision. Returns the created Revision.

    Never publishes; never touches the RootPage's title or slug.
    """
    site = Site.objects.filter(is_default_site=True).select_related('root_page').first()
    if site is None or site.root_page is None:
        raise HomePageNotFound('No default site (or site root page) is configured.')

    root = site.root_page
    # isinstance() would also match FlexPage (an MTI subclass of RootPage) --
    # we need the site root to be exactly a RootPage, not a promoted FlexPage.
    if root.specific_class is not RootPage:
        raise HomePageNotFound('Default site root page is not a RootPage.')

    root_specific = root.specific

    if not root_specific.permissions_for_user(user).can_edit():
        raise PromotePermissionDenied('User cannot edit the home page.')

    if root_specific.locked:
        raise HomePageLocked('Home page is locked and cannot be edited.')

    # The editor's latest state, not necessarily live -- falls back to the
    # live object itself when the FlexPage has no unpublished changes/revisions.
    source = flex_page.get_latest_revision_as_object()

    for field_name in PROMOTED_FIELDS:
        setattr(root_specific, field_name, getattr(source, field_name))

    return root_specific.save_revision(user=user, log_action=True, changed=True)
