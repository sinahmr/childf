from django.shortcuts import render
from main.utils import get_int
from main.constants import PROVINCES, GENDER


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
    return render(request, 'main/modify-child.html', {
        'user': None,
        'all_provinces': PROVINCES,
        'all_genders': GENDER
    })


def edit_child(request):
    user = {
        'first_name': 'علی',
        'last_name': 'علوی',
        'email': 'info@support.com',
        'gender': 'M',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg',
        'province': 'TEH',
        'accomplishments': 'کسب رتبه‌ی اول',
        'needs': [
            {
                'title': 'خرید فیفا ۹۹',
                'description': 'خرید بازی فیفا ۹۹',
                'cost': '۱۰۰۰',
                'urgent': True
            },
            {
                'title': 'خرید فیفا ۲۰۱۸',
                'description': 'خرید بازی فیفا ۲۰۱۸',
                'cost': '۱۵۰۰۰۰',
                'urgent': False
            }
        ]
    }
    return render(request, 'main/modify-child.html', {
        'user': user,
        'all_provinces': PROVINCES,
        'all_genders': GENDER
    })


def letter(request):
    child = {
        'name': 'علی احمدی',
    }
    return render(request, 'main/letter.html', {'child': child})


def login(request):
    return render(request, 'main/login.html', {})


def profile(request):
    user = {'first_name': 'علی',
            'last_name': 'علوی',
            'email': 'info@support.com',
            'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg',
            'province': 'تهران',
            'accomplishments': 'کسب رتبه‌ی اول'}
    return render(request, 'main/profile.html', {'user': user})


def send_request(request):
    child = {
        'name': 'علی احمدی',
    }
    return render(request, 'main/send-request.html', {'child': child})


def purchase(request):
    need_id = get_int(request.GET.get('need_id'))
    if need_id:
        # need = Need.objects.get(pk=need_id)
        need = {
            'child': {
                'name': 'علی احمدی'
            },
            'title': 'خرید فیفا ۲۰۱۸',
            'description': 'خرید بازی فیفا ۲۰۱۸',
            'cost': '۱۵۰۰۰۰'

        }
    else:
        need = None
    return render(request, 'main/purchase.html', {'need': need})
