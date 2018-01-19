import json

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core import mail
from django.shortcuts import render, Http404, get_object_or_404, HttpResponseRedirect

from main import forms, models
from django.contrib.auth import authenticate, login as django_login
from django.shortcuts import render, Http404, redirect
from main.constants import PROVINCES, GENDER
from main import models
from main.forms import ChildForm, DonorForm, VolunteerForm, UserInfoForm


def home(request):
    return render(request, 'main/base.html', {})


def volunteer(request):
    return render(request, 'main/children.html',
                  {'children': models.Child.objects.all(), 'show_all': True, 'user_type': 'donor'})


def child_information(request, child_id):
    child = get_object_or_404(models.Child, pk=child_id)
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
    if request.method == 'POST':
        user_form = None
        if user_class == 'admin' or user_class == 'donor':
            user_form = DonorForm(request.POST)
        if user_class == 'child':
            user_form = ChildForm(request.POST)
        if user_class == 'volunteer':
            user_form = VolunteerForm(request.POST)
        user_info_form = UserInfoForm(request.POST)
        if user_form.is_valid() and user_info_form.is_valid():
            user = user_form.save()
            user_info = user_info_form.save(commit=False)
            if request.FILES and request.FILES['image']:
                user_info.image = request.FILES['image']
            user_info.user = user
            user_info.save()
            needs_json = json.loads(request.POST['needs'])
            for need in needs_json['needs']:
                new_need = models.Need(title=need['title'], description=need['description'], cost=need['cost'])
                new_need.child = user
                new_need.save()
            print(needs_json)
            username = user_form.cleaned_data.get('email')
            raw_password = user_form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            django_login(request, user)
            return redirect('login')
        else:
            return render(request, 'main/modify-user.html', {
                'user': None,
                'all_provinces': PROVINCES,
                'all_genders': GENDER,
                'user_class': user_class,
                'user_type': '',
                'errors': [error for error in user_form.errors.values()] + [error for error in user_info_form.errors.values()],
            })
    # else:
    #     form = UserCreationForm()
    # return render(request, 'signup.html', {'form': form})
    else:
        return render(request, 'main/modify-user.html', {
            'user': None,
            'all_provinces': PROVINCES,
            'all_genders': GENDER,
            'user_class': user_class,
            'user_type': ''
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


@user_passes_test(lambda u: hasattr(u, 'child'))
def letter(request):
    if request.method == 'POST':
        form = forms.LetterForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['LetterTitle']
            content = form.cleaned_data['LetterContent']
            receiver = form.cleaned_data['LetterReceiverRadios']
            models.Letter.objects.create(**{
                'title': title,
                'content': content,
                'receiver': receiver,
                'verified': True if receiver == 'V' else None,
                'child': request.user.child
            })
            if receiver == 'V':
                emails = list()
                for support in models.Support.objects.filter(child=request.user.child):
                    emails.append(support.volunteer.email)
                mail.send_mail('نامه', '%s\n\n%s' % (title, content), 'childf.sut@gmail.com', emails)   # TODO email title
            return HttpResponseRedirect(request.path + '?success=1')
        else:
            return HttpResponseRedirect(request.path + '?success=0')
    else:
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
    if request.method == 'POST':
        verdict = request.POST.get('verdict')
        child_id = request.POST.get('child_id')
        child = get_object_or_404(models.Child, pk=child_id)
        if child.verified is None:
            child.verified = True if verdict == 'accept' else False
            child.save()
            return HttpResponse('OK')
        else:
            return HttpResponse('Already Done', status='400')
    else:
        return render(request, 'main/admin/children-approval.html',
                      {'children': models.Child.objects.filter(verified=None), 'user_type': 'admin'})


def admin_children(request):
    children = [{
        'name': 'علی احمدی',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg'
    }] * 10
    return render(request, 'main/children.html', {'children': children, 'show_all': True, 'user_type': 'admin'})


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
