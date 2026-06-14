"""Admin-menu organization for snippets.

Historically every snippet was registered with a bare ``register_snippet(Model)``
call in ``models.py``. That left 17 unrelated snippets in one flat, alphabetised
"Snippets" list, which is hard to navigate. Here we register each snippet through
a thin ``SnippetViewSet`` and bundle related ones into ``SnippetViewSetGroup``s so
the sidebar reads by topic (Subjects, Resources, Blog, Webinar Content, Reusable
Content). Models are unchanged — this is purely admin/menu wiring, no migrations.
"""
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from snippets.models import (
    Subject,
    K12Subject,
    SubjectCategory,
    FacultyResource,
    StudentResource,
    BlogCollection,
    BlogContentType,
    NewsSource,
    WebinarCollection,
    NoWebinarMessage,
    SharedContent,
    PromoteSnippet,
    AmazonBookBlurb,
    ContentWarning,
    RequireLoginMessage,
    Role,
    ErrataContent,
)


# --- Subjects --------------------------------------------------------------
class SubjectViewSet(SnippetViewSet):
    model = Subject
    icon = "tag"
    menu_label = "Subjects (HE)"
    list_display = ("name", "subject_color")


class K12SubjectViewSet(SnippetViewSet):
    model = K12Subject
    icon = "tag"
    menu_label = "K12 Subjects"
    list_display = ("name", "subject_category", "subject_color")
    list_filter = ("subject_category",)


class SubjectCategoryViewSet(SnippetViewSet):
    model = SubjectCategory
    icon = "tag"
    menu_label = "Subject Categories"
    list_display = ("subject", "subject_category")


class SubjectsGroup(SnippetViewSetGroup):
    menu_label = "Subjects"
    menu_icon = "tag"
    menu_order = 200
    items = (SubjectViewSet, K12SubjectViewSet, SubjectCategoryViewSet)


# --- Resources -------------------------------------------------------------
class FacultyResourceViewSet(SnippetViewSet):
    model = FacultyResource
    icon = "download"
    menu_label = "Faculty Resources"
    list_display = ("heading", "unlocked_resource", "creator_fest_resource", "resource_category")
    list_filter = ("unlocked_resource", "creator_fest_resource")


class StudentResourceViewSet(SnippetViewSet):
    model = StudentResource
    icon = "download"
    menu_label = "Student Resources"
    list_display = ("heading", "unlocked_resource", "resource_category")
    list_filter = ("unlocked_resource",)


class ResourcesGroup(SnippetViewSetGroup):
    menu_label = "Resources"
    menu_icon = "download"
    menu_order = 210
    items = (FacultyResourceViewSet, StudentResourceViewSet)


# --- Blog ------------------------------------------------------------------
class BlogCollectionViewSet(SnippetViewSet):
    model = BlogCollection
    icon = "edit"
    menu_label = "Blog Collections"
    list_display = ("name",)


class BlogContentTypeViewSet(SnippetViewSet):
    model = BlogContentType
    icon = "edit"
    menu_label = "Blog Content Types"
    list_display = ("content_type",)


class NewsSourceViewSet(SnippetViewSet):
    model = NewsSource
    icon = "edit"
    menu_label = "News Sources"
    list_display = ("name",)


class BlogGroup(SnippetViewSetGroup):
    menu_label = "Blog"
    menu_icon = "edit"
    menu_order = 220
    items = (BlogCollectionViewSet, BlogContentTypeViewSet, NewsSourceViewSet)


# --- Webinar content -------------------------------------------------------
# The Webinar *events* list lives in the webinars app (a ModelViewSet). These
# are the supporting snippets only.
class WebinarCollectionViewSet(SnippetViewSet):
    model = WebinarCollection
    icon = "media"
    menu_label = "Webinar Collections"
    list_display = ("name",)


class NoWebinarMessageViewSet(SnippetViewSet):
    model = NoWebinarMessage
    icon = "media"
    menu_label = "\"No Webinar\" Message"


class WebinarContentGroup(SnippetViewSetGroup):
    menu_label = "Webinar Content"
    menu_icon = "media"
    menu_order = 235
    items = (WebinarCollectionViewSet, NoWebinarMessageViewSet)


# --- Reusable site content -------------------------------------------------
class SharedContentViewSet(SnippetViewSet):
    model = SharedContent
    icon = "snippet"
    menu_label = "Shared Content"
    list_display = ("title", "heading")


class PromoteSnippetViewSet(SnippetViewSet):
    model = PromoteSnippet
    icon = "snippet"
    menu_label = "Promotions"
    list_display = ("name",)


class AmazonBookBlurbViewSet(SnippetViewSet):
    model = AmazonBookBlurb
    icon = "snippet"
    menu_label = "Amazon Book Blurb"


class ContentWarningViewSet(SnippetViewSet):
    model = ContentWarning
    icon = "warning"
    menu_label = "Content Warning"


class RequireLoginMessageViewSet(SnippetViewSet):
    model = RequireLoginMessage
    icon = "lock"
    menu_label = "Require-Login Message"


class RoleViewSet(SnippetViewSet):
    model = Role
    icon = "user"
    menu_label = "Roles"
    list_display = ("display_name", "salesforce_name")


class ErrataContentViewSet(SnippetViewSet):
    model = ErrataContent
    icon = "form"
    menu_label = "Errata Content"
    list_display = ("heading", "book_state")
    list_filter = ("book_state",)


class ReusableContentGroup(SnippetViewSetGroup):
    menu_label = "Reusable Content"
    menu_icon = "snippet"
    menu_order = 310
    items = (
        SharedContentViewSet,
        PromoteSnippetViewSet,
        AmazonBookBlurbViewSet,
        ContentWarningViewSet,
        RequireLoginMessageViewSet,
        RoleViewSet,
        ErrataContentViewSet,
    )


register_snippet(SubjectsGroup)
register_snippet(ResourcesGroup)
register_snippet(BlogGroup)
register_snippet(WebinarContentGroup)
register_snippet(ReusableContentGroup)


@hooks.register("construct_main_menu")
def hide_flat_snippets_menu(request, menu_items):
    # Every snippet now lives in a topical group above, so the catch-all flat
    # "Snippets" menu item just recreates the cluttered list we're replacing.
    # (Snippets remain accessible via their group and at /admin/snippets/.)
    menu_items[:] = [item for item in menu_items if item.name != "snippets"]
