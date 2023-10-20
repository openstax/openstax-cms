from django import forms

from wagtail.admin.widgets import AdminPageChooser
from wagtail.models import Page
from wagtail.admin import widgets as wagtailadmin_widgets


admin_page_params = {
    'can_choose_root': True,
    'show_edit_link': False,
    'user_perms': 'copy_to'
}


class ImportPage(forms.Form):
    """
    This form renders the import fields for zip archives.
    """

    file = forms.FileField(label="Zip Archive to Import")

    parent_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(**admin_page_params.copy()),
        label="Destination Parent Page",
        help_text="Imported pages will be created as children of this page."
    )

class ExportPage(forms.Form):
    """
    This form renders the export fields.
    """

    root_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(**admin_page_params.copy()),
        label="Root Page to Export",
        help_text="All children pages (including the selected root page) will be exported."
    )

    export_unpublished = forms.BooleanField(
        initial=True,
        required=False,
        label="Export Unpublished Pages",
        help_text="If True, unpublished pages will be exported along with published pages.",
    )

    null_pk = forms.BooleanField(
        widget=forms.HiddenInput(),
        required = False,
        initial=False,
        label="Remove Primary Keys",
        help_text="This is set to False as default and can be changed in code. Changing to True may break import functionality.",
    )

    null_fk = forms.BooleanField(
        initial=True,
        required=False,
        label="Remove Foreign Keys",
        help_text="If True, foreign keys will be nulled. Leave checked if exported archive will be imported to a different environment.",
    )

    null_users = forms.BooleanField(
        initial=True,
        required=False,
        label="Remove User References",
        help_text="If True, user fields (owner in pages, *user_id in images) will be nulled. Leave checked if exported archive will be imported to a different environment.",
    )

    export_images = forms.BooleanField(
        initial=True,
        required=False,
        label="Export Images",
        help_text="If True, image references will be nulled and images that are used on the page will be exported along with the rest of the content. Leave checked if exported archive will be imported to a different environment.",
    )

    export_documents = forms.BooleanField(
        initial=True,
        required=False,
        label="Export Documents",
        help_text="If True, document references will be nulled and documents that are used on the page will be exported along with the rest of the content. Leave checked if exported archive will be imported to a different environment.",
    )

    export_snippets = forms.BooleanField(
        initial=True,
        required=False,
        label="Export Snippets",
        help_text="If True, snippet references will be nulled and snippets that are used on the page will be exported along with the rest of the content. Leave checked if exported archive will be imported to a different environment.",
    )

    ignore_large_files = forms.BooleanField(
        initial=True,
        required=False,
        label="Exclude Large Files",
        help_text="If True, large files will be nullified and ignored during export.",
    )
