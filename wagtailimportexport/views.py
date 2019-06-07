import io
import json
import re

from zipfile import ZipFile

from django.http import JsonResponse, FileResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ungettext, ugettext_lazy as _
from django.http import HttpResponse

import requests

from wagtailimportexport.compat import messages, Page
from wagtailimportexport.exporting import (
    export_pages,
    zip_content,
)
from wagtailimportexport.forms import ExportForm, ImportFromFileForm, DuplicateForm
from wagtailimportexport.importing import (
    import_pages,
)


def index(request):
    return render(request, 'wagtailimportexport/index.html')

def duplicate(request, page):
    if request.method == 'POST':
        form = DuplicateForm(request.POST or None, user=request.user, page=page)
        if form.is_valid():
            try:
                allpages = {'pages' : export_pages(root_page=Page.objects.get(pk=page))}

                if len(allpages) > 1:
                    messages.error(request, _("More than one page cannot be duplicated at a time. Please duplicate a page that is not parent.s"))  
                else:
                    for (p_id, pdata) in enumerate(allpages['pages']):
                        allpages['pages'][p_id]["images"] = {}
                        allpages['pages'][p_id]["content"]["slug"] = form.cleaned_data['new_slug']
                        allpages['pages'][p_id]["content"]["title"] = form.cleaned_data['new_title']
                        allpages['pages'][p_id]["content"]["draft_title"] = form.cleaned_data['new_title']

                        for (f_id, fdata) in pdata["content"].items():
                            if type(fdata) == list:
                                for (f2_id, f2data) in enumerate(fdata):
                                    if 'pk' in f2data:
                                        allpages['pages'][p_id]["content"][f_id][f2_id]['pk'] = None


                parent_page = form.cleaned_data['new_parent_page']

                page_count, skipped_page_count = import_pages(allpages, parent_page, None)

                if not skipped_page_count:
                    messages.success(
                        request,
                        ungettext("%(count)s page duplicated.",
                                "%(count)s pages duplicated.", page_count) %
                        {'count': page_count})
                else:
                    messages.success(request, _("%(uploaded)s page(s) were duplicated while %(skipped)s page(s) were skipped because they were already in the environment.") % {'uploaded': page_count - skipped_page_count, 'skipped': skipped_page_count})

                return redirect('wagtailadmin_explore', parent_page.pk)

            except Page.DoesNotExist:
                messages.error(request, _("Duplicate failed because the root page was not found."))        

                return redirect('wagtailadmin_explore', page.pk)
    else:
        form = DuplicateForm(request.POST or None, user=request.user, page=page)

    return render(request, 'wagtailimportexport/duplicate.html', {
        'form': form,
        'pageid': page
    })


def import_from_file(request):
    """
    Import a part of a source site's page tree via an import of a JSON file
    exported to a user's filesystem from the source site's Wagtail Admin

    The source site's base url and the source page id of the point in the
    tree to import defined what to import and the destination parent page
    defines where to import it to.
    """
    if request.method == 'POST':
        form = ImportFromFileForm(request.POST, request.FILES)
        if form.is_valid():
            payload = io.BytesIO(form.cleaned_data['file'].read())
            parent_page = form.cleaned_data['parent_page']

            with ZipFile(payload, 'r') as zf:
                try:
                    with zf.open('content.json') as mf:
                        import_data = json.loads(mf.read().decode('utf-8-sig'))

                        page_count, skipped_page_count = import_pages(import_data, parent_page, zf)
                
                except LookupError as e:
                    messages.error(request, _("Import failed: %(reason)s") % {'reason': e})             

                else:
                    if not skipped_page_count:

                        messages.success(
                            request,
                            ungettext("%(count)s page imported.",
                                    "%(count)s pages imported.", page_count) %
                            {'count': page_count})
                    else:
                        messages.success(request, _("%(uploaded)s page(s) were uploaded while %(skipped)s page(s) were skipped because they were already in the environment.") % {'uploaded': page_count - skipped_page_count, 'skipped': skipped_page_count})

                return redirect('wagtailadmin_explore', parent_page.pk)
    else:
        form = ImportFromFileForm()

    return render(request, 'wagtailimportexport/import_from_file.html', {
        'form': form,
    })


def export_to_file(request):
    """
    Export a part of this source site's page tree, along with all snippets 
    and images, to a ZIP file on this user's filesystem for subsequent 
    import in a destination site's Wagtail Admin
    """
    if request.method == 'POST':
        form = ExportForm(request.POST)
        if form.is_valid():
            content_data = {
                'pages': export_pages(
                    root_page=form.cleaned_data['root_page'],
                    export_unpublished=form.cleaned_data['export_unpublished'],
                    null_users=form.cleaned_data['null_users'],
                    null_images=form.cleaned_data['null_images'],
                )
            }
            filedata = zip_content(content_data)
            payload = io.BytesIO(filedata)

            # Grab ZIP file from in-memory, make response with correct MIME-type
            response = HttpResponse(payload.getvalue(), content_type = "application/x-zip-compressed")
            # ..and correct content-disposition
            response['Content-Disposition'] = 'attachment; filename=content.zip'

            return response
    else:
        form = ExportForm()

    return render(request, 'wagtailimportexport/export_to_file.html', {
        'form': form,
    })
