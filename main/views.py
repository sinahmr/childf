from django.shortcuts import render


def home(request):
    return render(request, 'main/base.html', {})


def volunteer(request):
    children = [{
        'name': 'علی احمدی',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg'
    }] * 10
    return render(request, 'main/base-volunteer.html', {'children': children, 'show_all': True})


def child_information(request):
    return render(request, 'main/child-information.html', {})
