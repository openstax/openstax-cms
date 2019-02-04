from django import forms
from django.utils.translation import ugettext as _

from wagtailimportexport.compat import AdminPageChooser, Page, WAGTAIL_VERSION_2_OR_GREATER


admin_page_params = {
    'can_choose_root': True,
}

if WAGTAIL_VERSION_2_OR_GREATER:
    admin_page_params['user_perms'] = 'copy_to'


class ImportFromAPIForm(forms.Form):
    source_page_id = forms.IntegerField()
    source_site_base_url = forms.URLField()
    parent_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(**admin_page_params),
        label=_("Destination parent page"),
        help_text=_("Imported pages will be created as children of this page.")
    )


class ImportFromFileForm(forms.Form):
    file = forms.FileField(label=_("File to import"))
    parent_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(**admin_page_params),
        label=_("Destination parent page"),
        help_text=_("Imported pages will be created as children of this page.")
    )


class ExportForm(forms.Form):
    root_page = forms.ModelChoiceField(
        queryset=Page.objects.all(),
        widget=AdminPageChooser(can_choose_root=True),
    )
