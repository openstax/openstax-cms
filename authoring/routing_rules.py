# authoring/routing_rules.py
"""Routing-compliance rules for agent-created FlexPages.

Derived from the audit in docs/superpowers/notes/2026-06-05-routing-slug-audit.md.

Two hard facts about openstax.org routing drive this module:
  1. FlexPage URLs FLATTEN to /<slug> regardless of tree depth, and nginx, the
     frontend router, and the CMS API all resolve pages by slug GLOBALLY. So a
     slug must be unique across the ENTIRE page tree, not just among siblings.
  2. Certain top-level slugs are owned by nginx, 301 redirects, or the frontend
     router; a CMS page placed there is silently shadowed and never renders.

KNOWN GAP: the deploy-generated `uri-map` (highest-precedence 301s) is not in any
repo, so RESERVED_SLUGS may be incomplete. Backfill when that map is available.
"""
from wagtail.models import Page

# Agent-created FlexPages may only be created top-level under the single site root.
ALLOWED_PARENT_TYPES = frozenset({"pages.RootPage"})

# Top-level slugs owned by another layer (matched case-insensitively).
RESERVED_SLUGS = frozenset({
    # nginx -> Django backend
    "api", "ping", "admin", "django-admin", "blog-feed", "accounts", "oxauth",
    "documents", "images", "sitemap.xml", "l", "r",
    # nginx 301 redirects
    "give", "about-us", "technology", "creatorfest", "version",
    # frontend hard-coded routes (no CMS lookup)
    "home", "general", "books", "textbooks", "details", "errata", "adopters",
    "adoption", "blog", "campaign", "confirmation",
    "institutional-partnership-application", "interest", "renewal-form", "separatemap",
    # footer / legal
    "license", "tos", "privacy", "privacy-policy", "accessibility-statement", "careers",
    # CMS-owned canonical prefixes
    "k12", "subjects", "press", "news", "openstax-news",
    # frontend name-mismatch targets
    "edtech-partner-program", "foundation", "supporters",
})


class RoutingError(Exception):
    """Raised when a parent/slug is not a legal, routable location."""


def _parent_label(parent):
    specific = parent.specific
    return f"{type(specific)._meta.app_label}.{type(specific).__name__}"


def _suffix_against(taken, slug):
    """Return (effective_slug, collided_original_or_None) given a set of taken slugs."""
    if slug not in taken:
        return slug, None
    n = 1
    while f"{slug}-{n}" in taken:
        n += 1
    return f"{slug}-{n}", slug


def validate_page_location(parent, slug, *, exclude_page_id=None):
    """Validate a FlexPage can live at parent/slug per actual routing rules.

    Returns (effective_slug, warnings). Raises RoutingError for hard-illegal
    locations (reserved slug, or a parent that isn't the site root). Slug
    collisions are NOT hard errors: we suffix tree-globally and warn.
    `exclude_page_id` skips the page being updated so it doesn't collide with itself.
    """
    if slug.lower() in RESERVED_SLUGS:
        raise RoutingError(
            f"'{slug}' is a reserved route owned by nginx/redirects/the frontend; "
            "a page here would be silently shadowed. Choose another slug."
        )

    if _parent_label(parent) not in ALLOWED_PARENT_TYPES:
        raise RoutingError(
            "FlexPages may only be created at the top level under the site root "
            "(RootPage); deeper pages flatten to /<slug> and collide."
        )

    taken_qs = Page.objects.all()
    if exclude_page_id is not None:
        taken_qs = taken_qs.exclude(id=exclude_page_id)
    taken = set(taken_qs.values_list("slug", flat=True))

    effective_slug, collided = _suffix_against(taken, slug)
    warnings = []
    if collided is not None:
        existing = taken_qs.filter(slug=collided).first()
        warnings.append({
            "code": "slug_collision",
            "message": (
                f"A page with slug '{collided}' already exists in the site tree. "
                f"Created as '{effective_slug}' instead. Slugs are global on "
                "openstax.org — you probably want to UPDATE the existing page "
                "rather than create a duplicate."
            ),
            "existing_page_id": existing.id if existing else None,
            "existing_page_edit_url": f"/admin/pages/{existing.id}/edit/" if existing else None,
        })
    return effective_slug, warnings
