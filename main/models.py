from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import ugettext_lazy as _

from main.constants import LETTER_RECEIVER, GENDER, PROVINCES
from django.contrib.staticfiles.templatetags.staticfiles import static


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def name(self):
        return self.userinfo.first_name + ' ' + self.userinfo.last_name

    def user_type(self):
        if self.is_superuser:
            return 'admin'
        if hasattr(self, 'child'):
            return 'child'
        if hasattr(self, 'donor'):
            return 'donor'
        if hasattr(self, 'volunteer'):
            return 'volunteer'
        return 'anonymous'

    def persian_user_type(self):
        user_type = self.user_type()
        if user_type == 'admin':
            return 'مدیر'
        if user_type == 'child':
            return 'نیازمند'
        if user_type == 'donor':
            return 'همیار'
        if user_type == 'volunteer':
            return 'مددکار'
        return 'بازدیدکننده'

    def cast(self):
        if self.user_type() == 'admin':
            return self.donor
        if self.user_type() == 'child':
            return self.child
        if self.user_type() == 'donor':
            return self.donor
        if self.user_type() == 'volunteer':
            return self.volunteer

    def img_url(self):
        if self.userinfo.image:
            return self.userinfo.image.url
        return static('main/images/default-avatar.png')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


class AbstractUserInfo(models.Model):
    first_name = models.CharField(max_length=30, null=False)
    last_name = models.CharField(max_length=30, null=False)
    gender = models.CharField(max_length=1, choices=GENDER)
    year_of_birth = models.IntegerField()
    image = models.ImageField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)


class UserInfo(AbstractUserInfo):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class OngoingUserInfo(AbstractUserInfo):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مشخصات در دست تأیید'
        verbose_name_plural = 'مشخصات در دست تأیید'


class Child(User):
    province = models.CharField(max_length=3, choices=PROVINCES)
    verified = models.NullBooleanField(default=None)
    accomplishments = models.TextField(blank=True, null=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'نیازمند'
        verbose_name_plural = 'نیازمندان'

    def find_volunteer(self):
        try:
            return Support.objects.filter(child=self)[0].volunteer
        except:
            return Need


class Volunteer(User):
    objects = UserManager()

    class Meta:
        verbose_name = 'مددکار'
        verbose_name_plural = 'مددکاران'


class Donor(User):
    objects = UserManager()

    class Meta:
        verbose_name = 'همیار'
        verbose_name_plural = 'همیاران'


class Support(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, unique=True)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'حمایت'
        verbose_name_plural = 'حمایت‌ها'


class Sponsorship(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    sponsor = models.ForeignKey(Donor, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'کفالت'
        verbose_name_plural = 'کفالت‌ها'


class Letter(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False, null=False)
    content = models.TextField(blank=False, null=False)
    receiver = models.CharField(max_length=1, choices=LETTER_RECEIVER, blank=False, null=False)
    verified = models.NullBooleanField(default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نامه'
        verbose_name_plural = 'نامه‌ها'


class Need(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    cost = models.IntegerField(blank=False, null=False)
    resolved = models.BooleanField(default=False)
    urgent = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'نیاز'
        verbose_name_plural = 'نیازها'


class Purchase(models.Model):
    payer = models.ForeignKey(Donor, on_delete=models.CASCADE)
    amount = models.IntegerField(blank=False, null=False)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PurchaseForInstitute(Purchase):
    class Meta:
        verbose_name = 'پرداخت به مؤسسه'
        verbose_name_plural = 'پرداخت‌ها به مؤسسه'


class PurchaseForNeed(Purchase):
    need = models.ForeignKey(Need, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'پرداخت برای نیاز'
        verbose_name_plural = 'پرداخت‌ها برای نیاز'


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'فعالیت'
        verbose_name_plural = 'فعالیت‌ها'
