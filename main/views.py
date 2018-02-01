import json
import urllib

from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import password_reset
from django.core import mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, Http404, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import int_to_base36, base36_to_int

from main import models
from main.constants import PROVINCES, GENDER
from main.forms import ChildForm, DonorForm, VolunteerForm, UserInfoForm, LetterForm, RequestForm, PurchaseForm, OngoingUserInfoForm


# create users for different roles
# check different pages which need filters on children

def home(request):
    show_buttons = True
    if request.user.is_authenticated():
        show_buttons = False
    return render(request, 'main/home.html', {'show_buttons': show_buttons})


def show_children(request):
    show_all = request.GET.get('show_all', '1') == '1'
    children = models.Child.objects.all()
    sponsored_children = []
    supported_children = []
    if isinstance(request.user.cast(), models.Donor):
        sponsored_children = models.Child.objects.filter(sponsorship__sponsor=request.user.cast())
    if isinstance(request.user.cast(), models.Volunteer):
        supported_children = models.Child.objects.filter(support__volunteer=request.user.cast())
    if show_all == False:
        if isinstance(request.user.cast(), models.Donor):
            children = models.Child.objects.filter(sponsorship__sponsor=request.user.cast())
        if isinstance(request.user.cast(), models.Volunteer):
            children = models.Child.objects.filter(support__volunteer=request.user.cast())
    if request.user.user_type() == 'admin' and request.GET.get('without_donor', '0') == '1':
        show_all = False
        children = models.Child.objects.filter(sponsorship=None)
    return render(request, 'main/children.html',
                  {'children': children, 'sponsored_children': sponsored_children,
                   'supported_children': supported_children, 'show_all': show_all})


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
                  {'child': child,
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

            # Log Activity
            desc = 'کاربر %s (%s) اضافه شد' % (user.name(), user.persian_user_type())
            models.Activity.objects.create(user=request.user, description=desc)

            return render(request, 'main/modify-user.html', {
                'user': None,
                'all_provinces': PROVINCES,
                'all_genders': GENDER,
                'user_class': user_class,
                'success': '1',
            })
        else:
            errors = json.loads(user_form.errors.as_json())
            errors.update(json.loads(user_info_form.errors.as_json()))
            return render(request, 'main/modify-user.html', {
                'user': None,
                'all_provinces': PROVINCES,
                'all_genders': GENDER,
                'user_class': user_class,
                'errors': errors,
            })
    else:
        return render(request, 'main/modify-user.html', {
            'user': None,
            'all_provinces': PROVINCES,
            'all_genders': GENDER,
            'user_class': user_class
        })


def edit_user(request, user_id):
    if request.user.is_superuser:
        user = get_object_or_404(models.User, pk=user_id)
    else:
        if str(request.user.id) != user_id and (
                request.user.user_type() != 'volunteer' or not models.Child.objects.filter(
                support__volunteer=request.user.cast(), id=user_id).exists()):
            raise Http404
        user = get_object_or_404(models.User, pk=user_id)
    user = user.cast()
    if request.method == 'POST':
        if request.user.user_type() == 'admin' or request.user.user_type() == 'donor' and request.user == user:
            user_form = None
            user_class = user.user_type()
            if user_class == 'admin' or user_class == 'donor':
                user_form = DonorForm(request.POST, instance=user)
            if user_class == 'child':
                user_form = ChildForm(request.POST, instance=user)
            if user_class == 'volunteer':
                user_form = VolunteerForm(request.POST, instance=user)
            user_info_form = UserInfoForm(request.POST, instance=user.userinfo)
            if user_form.is_valid() and user_info_form.is_valid():
                new_user = user_form.save(commit=False)
                new_user.is_active = True
                new_user.save()
                new_user_info = user_info_form.save(commit=False)
                if request.FILES and request.FILES['image']:
                    new_user_info.image = request.FILES['image']
                needs_json = json.loads(request.POST['needs'])
                for need in needs_json['needs']:
                    if need['id'] == -1:
                        new_need = models.Need(title=need['title'], description=need['description'], cost=need['cost'], urgent=need['urgent'])
                        new_need.child = user
                    else:
                        new_need = models.Need.objects.get(id=int(need['id']))
                        new_need.urgent = need['urgent']
                    new_need.save()
                new_user_info.save()
                if user_class == 'child':
                    if request.POST['volunteer'] == '-1':
                        models.Support.objects.filter(child=new_user).delete()
                    elif models.Support.objects.filter(child=new_user).exists() and models.Support.objects.filter(child=new_user)[0].id != request.POST['volunteer']:
                        models.Support.objects.filter(child=new_user).delete()
                    if request.POST['volunteer'] != '-1' and not models.Support.objects.filter(child=new_user).exists():
                            models.Support.objects.create(child=new_user, volunteer=models.Volunteer.objects.get(id=request.POST['volunteer']))
                return render_modify_user_template(request, user, '2', None)
            else:
                errors = json.loads(user_form.errors.as_json())
                errors.update(json.loads(user_info_form.errors.as_json()))
                return render_modify_user_template(request, user, None, errors)
        elif request.user.user_type() == 'child' or request.user.user_type() == 'volunteer' and user.user_type() == 'volunteer':
            user_info_form = OngoingUserInfoForm(request.POST)
            if user_info_form.is_valid():
                new_user_info = user_info_form.save(commit=False)
                new_user_info.user = user
                if request.FILES and request.FILES['image']:
                    new_user_info.image = request.FILES['image']
                models.OngoingUserInfo.objects.filter(user=user).delete()
                new_user_info.save()
                return render_modify_user_template(request, user, '2', None)
            else:
                errors = json.loads(user_info_form.errors.as_json())
                return render_modify_user_template(request, user, None, errors)
            # TODO email to admin cause edit user info
        elif request.user.user_type() == 'volunteer':
            needs_json = json.loads(request.POST['needs'])
            for need in needs_json['needs']:
                if need['id'] == -1:
                    new_need = models.Need(title=need['title'], description=need['description'], cost=need['cost'], urgent=need['urgent'])
                    new_need.child = user
                else:
                    new_need = models.Need.objects.get(id=int(need['id']))
                    new_need.urgent = need['urgent']
                new_need.save()
            return render_modify_user_template(request, user, '2', None)
    else:
        return render_modify_user_template(request, user, None, None)


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

            # Log Activity
            dest = 'مددکار' if receiver == 'V' else 'همیاران'
            desc = 'نامه‌ای به %sش ارسال کرد' % dest
            models.Activity.objects.create(user=request.user, description=desc)

            if receiver == 'V':
                emails = list()
                for support in models.Support.objects.filter(child=request.user.child):
                    emails.append(support.volunteer.email)
                mail.send_mail('نامه', '%s\n\n%s' % (title, content), 'childf.sut@gmail.com', emails)  # TODO email title, CSS admin
            return HttpResponseRedirect(request.path + '?success=1')
        else:
            return HttpResponseRedirect(request.path + '?success=0')
    else:
        return render(request, 'main/letter.html', {'child': request.user.child})


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
            return render(request, 'main/login.html', {'error': 'آدرس ایمیل یا رمز عبور نادرست است.'})
    else:
        return render(request, 'main/login.html', {})


def forget(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = models.User.objects.get(email=email)
        except:
            return render(request, 'main/forget.html', {'error': 'ایمیل شما معتبر نمی‌باشد'})
        generator = PasswordResetTokenGenerator()
        token = generator.make_token(user)
        uidb36 = int_to_base36(user.pk)
        mail.send_mail('فراموشی رمز عبور',
                       request.build_absolute_uri(reverse('reset_password', kwargs={'uidb36': uidb36, 'token': token})),
                       'childf.sut@gmail.com',
                       [email])  # TODO Prettify
        return render(request, 'main/forget.html', {'success': 'ایمیل تایید فراموشی به شما ارسال شد'})
    else:
        return render(request, 'main/forget.html', {})


def reset_password(request, uidb36, token):
    generator = PasswordResetTokenGenerator()
    user_pk = base36_to_int(uidb36)
    try:
        user = models.User.objects.get(pk=user_pk)
    except models.User.DoesNotExist:
        user = None
    if generator.check_token(user, token):
        random_password = models.User.objects.make_random_password()
        user.set_password(random_password)
        user.save()
        mail.send_mail('فراموشی رمز عبور', 'password : %s' % random_password, 'childf.sut@gmail.com',
                       [user.email])  # TODO Prettify
        return render(request, 'main/forget.html', {'success': 'رمز عبور جدید شما به شما ایمیل شد'})
    else:
        return render(request, 'main/forget.html', {'error': 'کد فراموشی شما معتبر نمی‌باشد'})


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

            # Log Activity
            desc = 'برای مددکارش درخواستی ارسال کرد' % request.user.name()
            models.Activity.objects.create(user=request.user, description=desc)

            emails = list()
            for support in models.Support.objects.filter(child=request.user.child):
                emails.append(support.volunteer.email)
            mail.send_mail('درخواست', '%s\n\n%s' % (title, content), 'childf.sut@gmail.com', emails)  # TODO email title, CC admin
            return HttpResponseRedirect(request.path + '?success=1')
        else:
            return HttpResponseRedirect(request.path + '?success=0')
    else:
        return render(request, 'main/send-request.html', {'child': request.user.child})


def change_volunteer(request):
    if request.method == 'POST':
        # TODO: Send email!

        # Log Activity
        desc = 'علاقه به تغییر مددکار دارد' % request.user.name()
        models.Activity.objects.create(user=request.user, description=desc)

        return HttpResponse('OK')
    volunteer = request.user.cast().support_set.all()
    if len(volunteer):
        volunteer = volunteer[0].volunteer
    else:
        volunteer = None
    return render(request, 'main/change-volunteer.html', {
        'volunteer': volunteer
    })


@user_passes_test(lambda u: hasattr(u, 'child'))
def child_purchases(request):
    purchases = models.PurchaseForNeed.objects.filter(need__child=request.user.child)
    return render(request, 'main/child/purchases.html', {'purchases': purchases})


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def volunteer_letter_verification(request):
    letters = models.Letter.objects.filter(child__support__volunteer=request.user.volunteer, verified__isnull=True)
    return render(request, 'main/volunteer/letter-verification.html', {'letters': letters})


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def accept_letter(request, letter_id):
    letter = models.Letter.objects.filter(pk=letter_id).first()
    if letter:
        letter.verified = True
        letter.save()

        # Log Activity
        desc = 'نامه‌ی نیازمند %s به همیارانش را تایید کرد' % letter.child.name()
        models.Activity.objects.create(user=request.user, description=desc)

        emails = list()
        for sponsorship in models.Sponsorship.objects.filter(child=letter.child):
            emails.append(sponsorship.sponsor.email)
        mail.send_mail('نامه', '%s\n\n%s' % (letter.title, letter.content), 'childf.sut@gmail.com', emails)  # TODO email title
    return HttpResponseRedirect(reverse('volunteer_letter_verification'))


@user_passes_test(lambda user: user.user_type() == 'volunteer')
def decline_letter(request, letter_id):
    models.Letter.objects.filter(pk=letter_id).update(verified=False)

    # Log Activity
    desc = 'نامه‌ی نیازمند %s به همیارانش را رد کرد' % letter.child.name()
    models.Activity.objects.create(user=request.user, description=desc)

    return HttpResponseRedirect(reverse('volunteer_letter_verification'))


@user_passes_test(lambda u: hasattr(u, 'donor'))
def donor_purchases(request):
    institute_purchases = list(models.PurchaseForInstitute.objects.filter(payer=request.user.donor))
    need_purchases = list(models.PurchaseForNeed.objects.filter(payer=request.user.donor).prefetch_related('need__child'))
    for p in need_purchases:
        p.child_link = reverse('child_information', kwargs={'child_id': p.need.child.id})
    purchases = sorted(institute_purchases + need_purchases, key=lambda x: x.time, reverse=True)
    return render(request, 'main/donor/purchases.html', {'purchases': purchases})


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
                desc = 'مبلغ %d تومان برای نیاز %s از نیازمند %s پرداخت کرد' % (amount, need.title, need.child.name())
            else:
                models.PurchaseForInstitute.objects.create(**kwargs)
                desc = 'مبلغ %d تومان برای کمک به موسسه پرداخت کرد' % amount
            # Log Activity
            models.Activity.objects.create(user=request.user, description=desc)
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
        return render(request, 'main/purchase.html', {'need': need})


def activities(request):
    acts = models.Activity.objects.all()
    for act in acts:
        act.user_link = reverse('profile', kwargs={'user_id': act.user.id})
    return render(request, 'main/admin/activities.html', {'activities': acts})


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
    return render(request, 'main/admin/purchases.html', {'purchases': purchases})


@user_passes_test(lambda u: u.is_superuser)
def approval(request):
    if request.method == 'POST':
        verdict = request.POST.get('verdict')
        child_id = request.POST.get('child_id')
        child = get_object_or_404(models.Child, pk=child_id)
        if child.verified is None:
            child.verified = True if verdict == 'accept' else False
            child.save()

            # Log Activity
            desc = 'نیازمند %s %s شد' % (child.name(), 'تایید' if child.verified else 'رد')
            models.Activity.objects.create(user=request.user, description=desc)

            return HttpResponse('OK')
        else:
            return HttpResponse('Already Done', status='400')
    else:
        return render(request, 'main/admin/children-approval.html',
                      {'children': models.Child.objects.filter(verified=None)})


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
    if not user.is_authenticated():
        user_type = 'donor'
    else:
        user_type = user.user_type()
    if user_class == 'donor':
        return True
    if user_class == 'child':
        if user_type == 'volunteer' or user_type == 'admin':
            return True
    if user_class == 'volunteer':
        if user_type == 'admin':
            return True
    return False


def render_modify_user_template(request, user, success, errors, ):
    all_volunteers = []
    for vol in models.Volunteer.objects.all():
        all_volunteers.append({'id': vol.id, 'first_name': vol.userinfo.first_name, 'last_name': vol.userinfo.last_name})
    print(user.ongoinguserinfo_set.all())
    changed = False
    if user:
        if user.ongoinguserinfo_set.all() and len(user.ongoinguserinfo_set.all()) > 0:
            userinfo = user.ongoinguserinfo_set.all()[0]
            changed = True
        else:
            userinfo = user.userinfo
            changed = False
    return render(request, 'main/modify-user.html', {
        'user': user,
        'userinfo': userinfo,
        'all_provinces': PROVINCES,
        'all_genders': GENDER,
        'user_class': user.user_type(),
        'user_requested': request.user.user_type(),
        'all_volunteers': all_volunteers,
        'success': success,
        'errors': errors,
        'changed': changed,
    })


@user_passes_test(lambda u: u.is_superuser)
def commit_info(request, action, user_id):
    user = models.User.objects.get(id=user_id)
    user_info = user.userinfo
    if user.ongoinguserinfo_set and len(user.ongoinguserinfo_set.all()) > 0:
        ongoing = user.ongoinguserinfo_set.all()[0]
        if action == 'accept':
            user_info.first_name = ongoing.first_name
            user_info.last_name = ongoing.last_name
            user_info.gender = ongoing.gender
            user_info.year_of_birth = ongoing.year_of_birth
            user_info.image = ongoing.image
            user_info.save()
            ongoing.delete()
        elif action == 'reject':
            ongoing.delete()
    return HttpResponseRedirect(reverse('edit_user', kwargs={'user_id': user_id}))
