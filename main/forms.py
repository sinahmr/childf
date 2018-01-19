from django import forms
from django.forms import ModelForm

from main.constants import LETTER_RECEIVER
from main.models import Child, Donor, Volunteer, User, UserInfo


class LetterForm(forms.Form):
    LetterTitle = forms.CharField(required=True)
    LetterContent = forms.CharField(required=True)
    LetterReceiverRadios = forms.ChoiceField(choices=LETTER_RECEIVER, required=True)


class PurchaseForm(forms.Form):
    PurchaseAmount = forms.IntegerField(required=True)
    NeedID = forms.IntegerField(required=False)


class ChildForm(ModelForm):
    class Meta:
        model = Child
        exclude = ('date_joined', )


class DonorForm(ModelForm):
    class Meta:
        model = Donor
        exclude = ('date_joined', )


class VolunteerForm(ModelForm):
    class Meta:
        model = Volunteer
        exclude = ('date_joined', )


class UserInfoForm(ModelForm):
    class Meta:
        model = UserInfo
        exclude = ('user', )
