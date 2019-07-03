from django.shortcuts import redirect, render
from django.utils.translation import ungettext, ugettext_lazy as _

from wagtail.admin import messages
from wagtail.core.models import Page

from wagtailimportexport import exporting, importing

from duplicatebooks.forms import DuplicateForm


def duplicate(request, page):
    if request.method == 'POST':
        form = DuplicateForm(request.POST or None, user=request.user, page=page)
        if form.is_valid():
            try:
                
                export_settings = {'root_page': Page.objects.get(pk=page), 'export_unpublished': False, 
                'export_documents': False, 'export_images': False, 'null_pk': True,
                'null_fk': False, 'null_users': False}

                export_file = exporting.export_page(settings=export_settings)

                overwrite = {
                                'title': form.cleaned_data['new_title'], 
                                'draft_title': form.cleaned_data['new_title'], 
                                'slug': form.cleaned_data['new_slug']
                            }
                
                num_uploaded, num_failed, response = importing.import_page(export_file, form.cleaned_data['new_parent_page'], overwrites = overwrite)

                if not num_failed:
                    messages.success(
                        request,
                        ungettext("%(count)s book duplicated.",
                                "%(count)s books duplicated.", num_uploaded) %
                        {'count': num_uploaded})
                else:
                    messages.success(request, _("%(uploaded)s book(s) were duplicated while %(skipped)s page(s) were skipped because they were already in the environment. %(error)s") % {'uploaded': num_uploaded, 'skipped': num_failed, 'error': response})

                return redirect('wagtailadmin_explore', form.cleaned_data['new_parent_page'].pk)

            except Page.DoesNotExist:
                messages.error(request, _("Duplicate failed because the root book was not found."))        

                return redirect('wagtailadmin_explore', page.pk)
    else:
        form = DuplicateForm(request.POST or None, user=request.user, page=page)

    return render(request, 'duplicatebooks/duplicate.html', {
        'form': form,
        'pageid': page
    })