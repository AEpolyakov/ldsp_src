from django import forms
from .models import Department, Person, Record, Profile
from .consts import TYPE_CHOICES


class RecordForm(forms.Form):
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    time_from = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    time_to = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), required=False)
    person = forms.CharField(max_length=64)

    # class Meta:
    #     model = Record
    #     fields = ['person', ]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('user', )


class TimesheetForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class BaseOfRecords(forms.Form):
    name = forms.CharField(max_length=64, required=False)
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=False)
    department = forms.CharField(max_length=64, required=False)
