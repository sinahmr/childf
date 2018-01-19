from django import forms
from main.constants import LETTER_RECEIVER


class LetterForm(forms.Form):
    LetterTitle = forms.CharField(required=True)
    LetterContent = forms.CharField(required=True)
    LetterReceiverRadios = forms.ChoiceField(choices=LETTER_RECEIVER, required=True)


class PurchaseForm(forms.Form):
    PurchaseAmount = forms.IntegerField(required=True)
    NeedID = forms.IntegerField(required=False)
