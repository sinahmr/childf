from django.shortcuts import render


def home(request):
    return render(request, 'main/base.html', {})


def volunteer(request):
    return render(request, 'main/base-volunteer.html', {})


def child_information(request):
    return render(request, 'main/child-information.html', {})
