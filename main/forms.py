from django import forms
from django.forms import ModelForm

from main.constants import LETTER_RECEIVER
from main.models import Child, Donor, Volunteer, UserInfo, OngoingUserInfo


class LetterForm(forms.Form):
    LetterTitle = forms.CharField(required=True)
    LetterContent = forms.CharField(required=True)
    LetterReceiverRadios = forms.ChoiceField(choices=LETTER_RECEIVER, required=True)


class RequestForm(forms.Form):
    RequestTitle = forms.CharField(required=True)
    RequestContent = forms.CharField(required=True)


class PurchaseForm(forms.Form):
    PurchaseAmount = forms.IntegerField(required=True)
    NeedID = forms.IntegerField(required=False)


class ChildForm(ModelForm):
    class Meta:
        model = Child
        exclude = ('date_joined', 'password')


class DonorForm(ModelForm):
    class Meta:
        model = Donor
        exclude = ('date_joined', 'password')


class VolunteerForm(ModelForm):
    class Meta:
        model = Volunteer
        exclude = ('date_joined', 'password')


class UserInfoForm(ModelForm):
    class Meta:
        model = UserInfo
        exclude = ('user',)


class OngoingUserInfoForm(ModelForm):
    class Meta:
        model = OngoingUserInfo
        exclude = ('user', 'submit_date')
