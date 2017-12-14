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
    child = {
            'first_name': 'علی',
            'last_name': 'احمدی',
            'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg',
            'province': 'تهران',
            'accomplishments': 'کسب رتبه‌ی اول',
            'need_set': [{'id': 1,
                          'title': 'نیاز اول',
                          'description': 'کمک هزینه‌ی تحصیلی',
                          'cost': '۱۰۰',
                          'urgent': 'True',
                          'PurchaseForNeed_set': [{'id': 1,
                                                   'payer': 'حسن بیاتی',
                                                   'amount': '۲۰۰',
                                                   'time': '۲۰ فروردین ۱۹۹۶'}]
                          }]

        }
    return render(request, 'main/base-volunteer.html', {'child': child})


def add_child(request):
    return render(request, 'main/add-child.html', {})


def letter(request):
    child = {
        'name': 'علی احمدی',
    }
    return render(request, 'main/letter.html', {'child': child})


def login(request):
    return render(request, 'main/login.html', {})
