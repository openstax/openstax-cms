from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from wagtail.admin.widgets import AdminPageChooser
from wagtail.core.models import Page
from wagtail.admin import widgets as wagtailadmin_widgets


class DuplicateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # DuplicatePage must be passed a 'page' kwarg indicating the page to be copied
        try:
            self.page = Page.objects.get(pk=kwargs.pop('page'))
        except Page.DoesNotExist:
            raise Http404("No MyModel matches the given query.")

        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['new_title'] = forms.CharField(initial=self.page.title, label=_("New title"))
        self.fields['new_slug'] = forms.SlugField(initial=self.page.slug, label=_("New slug"))
        self.fields['new_parent_page'] = forms.ModelChoiceField(
            initial=self.page.get_parent(),
            queryset=Page.objects.all(),
            widget=wagtailadmin_widgets.AdminPageChooser(can_choose_root=True, user_perms='copy_to'),
            label=_("New parent page"),
            help_text=_("This copy will be a child of this given parent page.")
        )
        
        pages_to_copy = self.page.get_descendants(inclusive=True)
        subpage_count = pages_to_copy.count() - 1
        if subpage_count > 0:
            self.fields['copy_subpages'] = forms.BooleanField(
                required=False, initial=True, label=_("Copy subpages"),
                help_text=ungettext(
                    "This will copy %(count)s subpage.",
                    "This will copy %(count)s subpages.",
                    subpage_count) % {'count': subpage_count})

        can_publish = self.page.permissions_for_user(self.user).can_publish_subpage()

        if can_publish:
            pages_to_publish_count = pages_to_copy.live().count()
            if pages_to_publish_count > 0:
                # In the specific case that there are no subpages, customise the field label and help text
                if subpage_count == 0:
                    label = _("Publish copied page")
                    help_text = _("This page is live. Would you like to publish its copy as well?")
                else:
                    label = _("Publish copies")
                    help_text = ungettext(
                        "%(count)s of the pages being copied is live. Would you like to publish its copy?",
                        "%(count)s of the pages being copied are live. Would you like to publish their copies?",
                        pages_to_publish_count) % {'count': pages_to_publish_count}

                self.fields['publish_copies'] = forms.BooleanField(
                    required=False, initial=True, label=label, help_text=help_text
                )