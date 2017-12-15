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
    return render(request, 'main/children.html', {'children': children, 'show_all': True, 'user_type': 'donor'})


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
    return render(request, 'main/child-information.html', {'child': child, 'user_type': 'child'})


def add_child(request):
    return render(request, 'main/modify-child.html', {
        'user': None,
        'all_provinces': PROVINCES,
        'all_genders': GENDER,
        'user_type': 'volunteer'
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
    return render(request, 'main/letter.html', {'child': child, 'user_type': 'child'})


def login(request):
    return render(request, 'main/login.html', {})


def profile(request):
    user = {'first_name': 'علی',
            'last_name': 'علوی',
            'email': 'info@support.com',
            'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg',
            'province': 'تهران',
            'accomplishments': 'کسب رتبه‌ی اول'}
    return render(request, 'main/profile.html', {'user': user, 'user_type': 'child'})


def send_request(request):
    child = {
        'name': 'علی احمدی',
    }
    return render(request, 'main/send-request.html', {'child': child, 'user_type': 'child'})


def change_volunteer(request):
    return render(request, 'main/change-volunteer.html', {
        'volunteer_name': 'کریم بنزما',
        'user_type': 'child'
    })


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
    return render(request, 'main/purchase.html', {'need': need, 'user_type': 'donor'})


def activities(request):
    activities = [
                     {'date': '۲۴ آذر ۱۳۹۶', 'user': 'علی حسینی (مددکار)',
                      'description': 'اضافه کردن نیازمند: امین رضازاده'},
                     {'date': '۲۴ آذر ۱۳۹۶', 'user': 'حسین علی زاده (مددکار)',
                      'description': 'اضافه کردن نیازمند: رضا امین‌زاده'}
                 ] * 3
    activities += [
                      {'date': '۲۳ آذر ۱۳۹۶', 'user': 'قلی قلی‌زاده (همیار)',
                       'description': 'پراخت نیاز'},
                      {'date': '۲۳ آذر ۱۳۹۶', 'user': 'امین امینی (همیار)',
                       'description': 'تحت کفالت قرار دادن'}
                  ] * 2
    return render(request, 'main/admin/activities.html', {'activities': activities, 'user_type': 'admin'})


def admin_purchases(request):
    purchases = [
                    {'date': '۲۴ آذر ۱۳۹۶', 'donor': 'علی حسینی',
                     'need': 'هزینه ثبت نام', 'need_amount': 10000, 'child': 'رضا امین زاده'},
                    {'date': '۲۴ آذر ۱۳۹۶', 'donor': 'حسن حسینی',
                     'need': 'هزینه بیمارستان', 'need_amount': 30000, 'child': 'رضا امین زاده'},
                ] * 3
    purchases += [
                     {'date': '۲۳ آذر ۱۳۹۶', 'donor': 'علی قلی زاده',
                      'need': 'هزینه مسکن', 'need_amount': 122300, 'child': 'هادی فضلی'},
                     {'date': '۲۳ آذر ۱۳۹۶', 'donor': 'سارا رضایی',
                      'need': 'هزینه بیمه', 'need_amount': 1002000, 'child': 'سینا امینی'},
                 ] * 3
    purchases += [
        {'date': '۲۲ آذر ۱۳۹۶', 'donor': 'علی قلی زاده',
         'need': '', 'need_amount': 122300, 'child': 'موسسه'},
        {'date': '۲۲ آذر ۱۳۹۶', 'donor': 'سارا رضایی',
         'need': '', 'need_amount': 1002000, 'child': 'موسسه'},
    ]
    return render(request, 'main/admin/purchases.html', {'purchases': purchases, 'user_type': 'admin'})


def approval(request):
    children = [{
        'id': child_id,
        'name': 'علی احمدی',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg'
    } for child_id in range(1, 10)]
    return render(request, 'main/admin/children-approval.html', {'children': children, 'user_type': 'admin'})


def admin_children(request):
    children = [{
        'name': 'علی احمدی',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg'
    }] * 10
    return render(request, 'main/children.html', {'children': children, 'show_all': True, 'user_type': 'admin'})
