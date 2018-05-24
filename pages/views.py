from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .models import (GeneralPage,
                     HomePage,
                     HigherEducation,
                     AboutUs,
                     EcosystemAllies,
                     ContactUs,
                     FoundationSupport,
                     OurImpact,
                     Give,
                     TermsOfService,
                     AP,
                     FAQ,
                     Support,
                     GiveForm,
                     Accessibility,
                     Licensing,
                     CompCopy,
                     AdoptForm,
                     InterestForm,
                     Marketing,
                     Technology,
                     ErrataList,
                     PrivacyPolicy,
                     PrintOrder)


@csrf_exempt
def page_detail(request, slug):
    """
    Redirects the page api to the Wagtail API. This should eventually be removed as the FE moves to the new /api/v2/ endpoint
    """
    page_found = True

    try:
        page = HomePage.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except HomePage.DoesNotExist:
        page_found = False

    try:
        page = HigherEducation.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except HigherEducation.DoesNotExist:
        page_found = False

    try:
        page = GeneralPage.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except GeneralPage.DoesNotExist:
        page_found = False

    try:
        page = AboutUs.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except AboutUs.DoesNotExist:
        page_found = False

    try:
        page = EcosystemAllies.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except EcosystemAllies.DoesNotExist:
        page_found = False

    try:
        page = ContactUs.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except ContactUs.DoesNotExist:
        page_found = False

    try:
        page = FoundationSupport.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except FoundationSupport.DoesNotExist:
        page_found = False

    try:
        page = OurImpact.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except OurImpact.DoesNotExist:
        page_found = False

    try:
        page = Give.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Give.DoesNotExist:
        page_found = False

    try:
        page = TermsOfService.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except TermsOfService.DoesNotExist:
        page_found = False

    try:
        page = AP.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except AP.DoesNotExist:
        page_found = False

    try:
        page = FAQ.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except FAQ.DoesNotExist:
        page_found = False

    try:
        page = Support.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Support.DoesNotExist:
        page_found = False

    try:
        page = GiveForm.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except GiveForm.DoesNotExist:
        page_found = False

    try:
        page = Accessibility.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Accessibility.DoesNotExist:
        page_found = False

    try:
        page = Licensing.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Licensing.DoesNotExist:
        page_found = False

    try:
        page = CompCopy.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except CompCopy.DoesNotExist:
        page_found = False

    try:
        page = AdoptForm.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except AdoptForm.DoesNotExist:
        page_found = False

    try:
        page = InterestForm.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except InterestForm.DoesNotExist:
        page_found = False

    try:
        page = Marketing.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Marketing.DoesNotExist:
        page_found = False

    try:
        page = Technology.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except Technology.DoesNotExist:
        page_found = False

    try:
        page = ErrataList.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except ErrataList.DoesNotExist:
        page_found = False

    try:
        page = PrivacyPolicy.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except PrivacyPolicy.DoesNotExist:
        page_found = False

    try:
        page = PrintOrder.objects.get(slug=slug)
        return redirect('/api/v2/pages/{}'.format(page.pk))
    except PrintOrder.DoesNotExist:
        page_found = False

    if not page_found:
        return HttpResponse(status=404)
