from django.shortcuts import redirect


def handle_page_not_found_404(request):
    return redirect('/404')
