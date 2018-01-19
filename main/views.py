from django.shortcuts import render, Http404, get_object_or_404
from main.constants import PROVINCES, GENDER
from main.models import Child
from main import models


def home(request):
    return render(request, 'main/base.html', {})


def volunteer(request):
    return render(request, 'main/children.html',
                  {'children': Child.objects.all(), 'show_all': True, 'user_type': 'donor'})


def child_information(request, child_id):
    child = get_object_or_404(Child, pk=child_id)
    child2 = {
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


def add_user(request, user_class):
    if user_class not in ['admin', 'child', 'volunteer', 'donor']:
        raise Http404("User type is not valid!")
    return render(request, 'main/modify-user.html', {
        'user': None,
        'all_provinces': PROVINCES,
        'all_genders': GENDER,
        'user_class': user_class,
        'user_type': 'admin'
    })


def modify_user(request, user_class):
    if user_class not in ['admin', 'child', 'volunteer', 'donor']:
        raise Http404("User type is not valid!")
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
    return render(request, 'main/modify-user.html', {
        'user': user,
        'all_provinces': PROVINCES,
        'all_genders': GENDER,
        'user_class': user_class,
        'user_type': 'admin'
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


def child_purchases(request):
    purchases = [
                    {
                        'time': '۲۴ آذر ۱۳۹۶',
                        'amount': '۱۲۳۰۰۰',
                        'need': {
                            'title': 'خرید فیفا ۲۰۱۸'
                        },
                    },
                    {
                        'time': '۲۵ آذر ۱۳۹۶',
                        'amount': '۱۲۰۰۰۰',
                        'need': {
                            'title': 'خرید PES ۲۰۱۸'
                        },
                    }
                ] * 5
    return render(request, 'main/child/purchases.html', {'purchases': purchases, 'user_type': 'child'})


def volunteer_letter_verification(request):
    letters = [
        {
            'id': letter_id,
            'child': {
                'first_name': 'انگولو',
                'last_name': 'کانته'
            },
            'title': 'چطوری همیارم؟',
            'content': 'همیار جان من فلانی هستم.\nحالت چطور است؟',
            'date': '۲ آذر ۱۳۹۶'
        } if letter_id % 2 == 1 else
        {
            'id': letter_id,
            'child': {
                'first_name': 'تیمو',
                'last_name': 'باکایوکو'
            },
            'title': 'ناتاناییل؟',
            'content': 'ناتانائیل،آرزو مکن که خدا را جز در همه جا بیابی.\nخب؟',
            'date': '۲ آبان ۱۳۹۶'
        } for letter_id in range(1, 10)]
    return render(request, 'main/volunteer/letter-verification.html', {'letters': letters, 'user_type': 'volunteer'})


def donor_purchases(request):
    purchases = [
                    {
                        'time': '۲۴ آذر ۱۳۹۶',
                        'amount': '۱۲۳۰۰۰',
                        'need': {
                            'title': 'خرید فیفا ۲۰۱۸',
                            'child': {
                                'first_name': 'تیمو',
                                'last_name': 'باکایوکو'
                            }
                        },
                    },
                    {
                        'time': '۲۵ آذر ۱۳۹۶',
                        'amount': '۱۲۰۰۰۰',
                        'need': {
                            'title': 'خرید PES ۲۰۱۸',
                            'child': {
                                'first_name': 'انگولو',
                                'last_name': 'کانته'
                            }
                        },
                    }
                ]
    return render(request, 'main/donor/purchases.html', {'purchases': purchases, 'user_type': 'donor'})


def purchase(request):
    need_id = request.GET.get('need_id')
    if need_id:
        need = get_object_or_404(models.Need, pk=need_id)
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
    return render(request, 'main/admin/children-approval.html', {'children': Child.objects.all(), 'user_type': 'admin'})


def admin_children(request):
    return render(request, 'main/children.html',
                  {'children': Child.objects.all(), 'show_all': True, 'user_type': 'admin'})


def sponsored_children(request):
    children = [{
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

        }] * 5
    return render(request, 'main/sponsored-children.html', {'children': children, 'user_type': 'child'})


def admin_unresolveds(request):
    needs = [
        {
            'title': 'خرید فیفا ۹۹',
            'description': 'خرید بازی فیفا ۹۹',
            'cost': '۱۰۰۰',
            'urgent': True,
            'child': 'علی احمدی',
        },
        {
            'title': 'خرید فیفا ۲۰۱۸',
            'description': 'خرید بازی فیفا ۲۰۱۸',
            'cost': '۱۵۰۰۰۰',
            'urgent': False,
            'child': 'علی احمدی',
        }
    ] * 3
    return render(request, 'main/admin/unresolveds.html', {'needs': needs, 'user_type': 'admin'})


def admin_volunteers(request):
    volunteers = [
        {
            'name': 'علی رضایی',
            'child_count': 4,
        },
        {
            'name': 'محمد محمدی',
            'child_count': 3,
        },
        {
            'name': 'مهدی میرزایی',
            'child_count': 2,
        },
    ]
    return render(request, 'main/admin/volunteers.html', {'volunteers': volunteers, 'user_type': 'admin'})
