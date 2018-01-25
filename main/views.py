import json
import urllib

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import user_passes_test
from django.core import mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, Http404, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse

from main import models
from main.constants import PROVINCES, GENDER
from main.forms import ChildForm, DonorForm, VolunteerForm, UserInfoForm, LetterForm, RequestForm, PurchaseForm


# create users for different roles
# check different pages which need filters on children

def home(request):
    return render(request, 'main/home.html', {})


def volunteer(request):
    show_all = request.GET.get('show_all', '1') == '1'
    children = models.Child.objects.all()
    if show_all == False:
        if isinstance(request.user.cast(), models.Donor):
            children = models.Child.objects.filter(sponsorship__sponsor=request.user.cast())
        if isinstance(request.user.cast(), models.Volunteer):
            children = models.Child.objects.filter(support__volunteer=request.user.cast())

    return render(request, 'main/children.html',
                  {'children': children, 'show_all': show_all, 'user_type': 'donor'})


def child_information(request, child_id):
    child = get_object_or_404(models.Child, pk=child_id)
    user = request.user.cast()
    has_sponsorship = isinstance(user, models.Donor) and models.Sponsorship.objects.filter(child=child,
                                                                                           sponsor=user).exists()
    has_support = isinstance(user, models.Volunteer) and models.Support.objects.filter(child=child,
                                                                                       volunteer=user).exists()
    if request.method == 'POST':
        if request.POST['action'] == 'sponsorship':
            if not has_sponsorship:
                sponsorship = models.Sponsorship(child=child, sponsor=user)
                sponsorship.save()
                has_sponsorship = True
            else:
                models.Sponsorship.objects.get(child=child, sponsor=user).delete()
                has_sponsorship = False
        if request.POST['action'] == 'support':
            if not has_support:
                support = models.Support(child=child, volunteer=user)
                support.save()
                has_support = True
            else:
                models.Support.objects.get(child=child, volunteer=user).delete()
                has_support = False
    child2 = {
        'first_name': 'علی',
        'last_name': 'احمدی',
        'img_url': 'https://www.understood.org/~/media/f7ffcd3d00904b758f2e77e250d529dc.jpg',
        'province': 'تهران',
        'accomplishments': 'کسب رتبه‌ی اول',
        'need_set': {'all': [{'id': 1,
                      'title': 'نیاز اول',
                      'description': 'کمک هزینه‌ی تحصیلی',
                      'cost': '۱۰۰',
                      'urgent': 'True',
                      'PurchaseForNeed_set': [{'id': 1,
                                               'payer': 'حسن بیاتی',
                                               'amount': '۲۰۰',
                                               'time': '۲۰ فروردین ۱۹۹۶'}]
                              }]}
    }
    return render(request, 'main/child-information.html',
                  {'child': child, 'user_type': 'child',
                   'has_sponsorship': has_sponsorship,
                   'has_support': has_support})


def add_user(request, user_class):
    if user_class not in ['admin', 'child', 'volunteer', 'donor'] or not is_authorized_for_add_user(request.user, user_class):
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
                new_need = models.Need(title=need['title'], description=need['description'], cost=need['cost'], urgent=need['urgent'])
                new_need.child = user
                new_need.save()
            username = user_form.cleaned_data.get('email')
            raw_password = request.POST.get('password')
            user.set_password(raw_password)
            user.is_active = True
            user.save()
            authenticate(username=username, password=raw_password)
            return render(request, 'main/modify-user.html', {
                'user': None,
                'all_provinces': PROVINCES,
                'all_genders': GENDER,
                'user_class': user_class,
                'success': True,
            })
        else:
            errors = json.loads(user_form.errors.as_json())
            errors.update(json.loads(user_info_form.errors.as_json()))
            return render(request, 'main/modify-user.html', {
                'user': None,
                'all_provinces': PROVINCES,
                'all_genders': GENDER,
                'user_class': user_class,
                'user_type': '',
                'errors': errors,
            })
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


@user_passes_test(lambda user: user.user_type() == 'child')
def letter(request):
    if request.method == 'POST':
        form = LetterForm(request.POST)
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
        return render(request, 'main/letter.html', {'child': request.user.child, 'user_type': 'child'})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = models.User.objects.get(email=email)
            if not user.check_password(password):
                raise Exception
            django_login(request, user)
            return redirect('home')
        except:
            return render(request, 'main/login.html', {'error': 'نام کاربری یا رمز عبور نادرست است.'})
    else:
        return render(request, 'main/login.html', {})


def logout(request):
    django_logout(request)
    return redirect('home')


def profile(request, user_id):
    if request.user.is_superuser:
        user = get_object_or_404(models.User, pk=user_id)
    else:
        if str(request.user.id) != user_id:
            raise Http404
        user = request.user
    return render(request, 'main/profile.html', {'user': user})


@user_passes_test(lambda u: hasattr(u, 'child'))
def send_request(request):
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['RequestTitle']
            content = form.cleaned_data['RequestContent']
            emails = list()
            for support in models.Support.objects.filter(child=request.user.child):
                emails.append(support.volunteer.email)
            mail.send_mail('درخواست', '%s\n\n%s' % (title, content), 'childf.sut@gmail.com', emails)   # TODO email title
            return HttpResponseRedirect(request.path + '?success=1')
        else:
            return HttpResponseRedirect(request.path + '?success=0')
    else:
        return render(request, 'main/send-request.html', {'child': request.user.child, 'user_type': 'child'})


def change_volunteer(request):
    return render(request, 'main/change-volunteer.html', {
        'volunteer_name': 'کریم بنزما',
        'user_type': 'child'
    })


@user_passes_test(lambda u: hasattr(u, 'child'))
def child_purchases(request):
    purchases = models.PurchaseForNeed.objects.filter(need__child=request.user.child)
    return render(request, 'main/child/purchases.html', {'purchases': purchases, 'user_type': 'child'})


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def volunteer_letter_verification(request):
    letters = models.Letter.objects.filter(child__support__volunteer=request.user.volunteer, verified__isnull=True)
    return render(request, 'main/volunteer/letter-verification.html', {'letters': letters, 'user_type': 'volunteer'})


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def accept_letter(request, letter_id):
    letter = models.Letter.objects.filter(pk=letter_id).first()
    if letter:
        letter.verified = True
        letter.save()
        emails = list()
        for sponsorship in models.Sponsorship.objects.filter(child=letter.child):
            emails.append(sponsorship.sponsor.email)
        mail.send_mail('نامه', '%s\n\n%s' % (letter.title, letter.content), 'childf.sut@gmail.com', emails)  # TODO email title
    return HttpResponseRedirect(reverse('volunteer_letter_verification'))


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def decline_letter(request, letter_id):
    models.Letter.objects.filter(pk=letter_id).update(verified=False)
    return HttpResponseRedirect(reverse('volunteer_letter_verification'))


@user_passes_test(lambda u: hasattr(u, 'donor'))
def donor_purchases(request):
    institute_purchases = list(models.PurchaseForInstitute.objects.filter(payer=request.user.donor))
    need_purchases = list(models.PurchaseForNeed.objects.filter(payer=request.user.donor).prefetch_related('need__child'))
    for p in need_purchases:
        p.child_link = reverse('child_information', kwargs={'child_id': p.need.child.id})
    purchases = sorted(institute_purchases + need_purchases, key=lambda x: x.time, reverse=True)
    return render(request, 'main/donor/purchases.html', {'purchases': purchases, 'user_type': 'donor'})


@user_passes_test(lambda u: hasattr(u, 'donor'))
def purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        params = request.GET.copy()
        if form.is_valid():
            need_id = form.cleaned_data['NeedID']
            amount = form.cleaned_data['PurchaseAmount']
            kwargs = {
                'payer': request.user.donor,
                'amount': amount
            }
            if need_id:
                need = get_object_or_404(models.Need, pk=need_id)
                models.PurchaseForNeed.objects.create(**kwargs, need=need)
            else:
                models.PurchaseForInstitute.objects.create(**kwargs)
            return HttpResponseRedirect(reverse('bank') + '?redirect_url=%s' % urllib.parse.quote_plus(
                reverse('donor_purchase') + '?%s' % ('need_id=' + str(need_id) if need_id else '')) + '&amount=%s' % amount)
        else:
            params.update({'success': '0'})
            return HttpResponseRedirect(request.path + '?' + params.urlencode())
    else:
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


@user_passes_test(lambda u: u.is_superuser)
def admin_purchases(request):
    institute_purchases = list(models.PurchaseForInstitute.objects.all())
    need_purchases = list(models.PurchaseForNeed.objects.all().prefetch_related('need__child'))
    for p in need_purchases:
        p.child_link = reverse('child_information', kwargs={'child_id': p.need.child.id})
    purchases = institute_purchases + need_purchases
    for p in purchases:
        p.donor_link = reverse('profile', kwargs={'user_id': p.payer.donor.id})
    purchases = sorted(purchases, key=lambda x: x.time, reverse=True)
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
    return render(request, 'main/children.html',
                  {'children': models.Child.objects.all(), 'show_all': True, 'user_type': 'admin'})


@user_passes_test(lambda user: user.is_superuser)
def admin_unresolveds(request):
    needs = models.Need.objects.filter(resolved=False)
    return render(request, 'main/admin/unresolveds.html', {'needs': needs})


def admin_volunteers(request):
    volunteers = models.Volunteer.objects.all().annotate(child_count=Count('support'))
    return render(request, 'main/admin/volunteers.html', {'volunteers': volunteers})


def bank(request):
    redirect_url = urllib.parse.unquote(request.GET.get('redirect_url'))
    amount = request.GET.get('amount') + '0'
    if '?' not in redirect_url:
        redirect_url += '?'
    success = True
    redirect_url += '&success=1'
    return render(request, 'main/bank.html', {'success': success, 'redirect_url': redirect_url, 'amount': amount})


def is_authorized_for_add_user(user, user_class):
    if user_class == 'donor':
        return True
    if user_class == 'child':
        if user.__class__ == 'Volunteer' or user.is_superuser:
            return True
    if user_class == 'volunteer':
        if user.is_superuser:
            return True
    return False
