from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ngettext
from django.http import HttpResponse

from wagtail.admin import messages

from wagtailimportexport import forms, importing, exporting


def index(request):
    """
    View for main menu of the Import/Export tool. Provides a list
    of features.
    """
    return render(request, 'wagtailimportexport/index.html')

def import_page(request):
    """
    View for the import page.
    """
    if request.method == 'POST':
        form = forms.ImportPage(request.POST, request.FILES)

        if form.is_valid():

            # Read fields on the submitted form.
            form_file = form.cleaned_data['file']
            form_parentpage = form.cleaned_data['parent_page']

            # Import pages and get the response.
            num_uploaded, num_failed, response = importing.import_page(form_file, form_parentpage)

            # Show messages depending on the response.
            if not num_failed:
                # All pages are imported.
                messages.success(
                    request, ngettext("Imported %(count)s page.", "Imported %(count)s pages.", num_uploaded)
                    % {'count': num_uploaded}
                )
            elif not num_uploaded:
                # None of the pages are imported.
                messages.error(
                    request, ngettext("Failed to import %(count)s page. %(reason)s", "Failed to import %(count)s pages. %(reason)s", num_failed)
                    % {'count': num_failed, 'reason': response}
                )
            else:
                # Some pages are imported and some failed.
                messages.warning(
                    request, ngettext("Failed to import %(failed)s out of %(total)s page. %(reason)s", "Failed to import %(failed)s out of %(total)s pages. %(reason)s", num_failed + num_uploaded)
                    % {'failed': num_failed, 'total': num_failed + num_uploaded, 'reason': response}
                )

            # Redirect client to the parent page view on admin.
            return redirect('wagtailadmin_explore', form_parentpage.pk)
    else:
        form = forms.ImportPage()
        
        # Redirect client to form.
        return render(request, 'wagtailimportexport/import-page.html', {
            'form': form,
        })

def export_page(request):
    """
    View for the export page.
    """

    if request.method == 'POST':
        form = forms.ExportPage(request.POST)

        if form.is_valid():
            export_file = exporting.export_page(settings=form.cleaned_data)

            if export_file:
                # Grab ZIP file from in-memory, make response with correct MIME-type
                response = HttpResponse(export_file.getvalue(), content_type = "application/x-zip-compressed")
                
                # ..and correct content-disposition
                response['Content-Disposition'] = 'attachment; filename=wagtail-export.zip'

                return response
            else:
                form = forms.ExportPage()

                messages.error(
                    request, "Failed to generate an export file. Please refer to the logs for further details."
                )

                # Redirect client to form.
                return render(request, 'wagtailimportexport/export-page.html', {
                    'form': form,
                })

    else:
        form = forms.ExportPage()

        # Redirect client to form.
        return render(request, 'wagtailimportexport/export-page.html', {
            'form': form,
        })
