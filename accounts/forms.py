from datetime import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from accounts.models import UserProfile, GENDER_CHOICES

CURRENT_YEAR = datetime.utcnow().year
BIRTH_YEAR_CHOICES = [year for year in range(CURRENT_YEAR-90, CURRENT_YEAR-13)]


class SignUpForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Create username'}), max_length=30, required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}), max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}), max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}), max_length=254, required=True, help_text='A valid email address, please.')
    birth_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=BIRTH_YEAR_CHOICES,
            attrs={
                'data-date-format': 'yyyy/mm/dd',
                'class': 'form-control snps-inline-select select-date-widget'
            },
            empty_label=("Choose Year", "Choose Month", "Choose Day")
        ),
        help_text='Birth date.'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}),
        max_length=30,
        required=True,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Reenter password'}),
        max_length=30,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'birth_date',
            'email',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your first name'}), max_length=30,
        required=False)
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your last name'}), max_length=30,
        required=False)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}), max_length=254,
        required=True)
    location = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your city, country'}), max_length=30,
        required=False)
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Please, add a few words about yourself.'}), max_length=500,
        required=False)
    website = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Link to your website'}), max_length=254,
        required=False)
    birth_date = forms.DateField(
        widget=forms.SelectDateWidget(
            years=BIRTH_YEAR_CHOICES,
            attrs={
                'data-date-format': 'yyyy/mm/dd',
                'class': 'form-control snps-inline-select select-date-widget'
            },
            empty_label=("Choose Year", "Choose Month", "Choose Day")
        ),
        help_text='Birth date.'
    )
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect(attrs={'class': 'gender-select'}))

    def __init__(self, *args, **kw):
        super(UserProfileForm, self).__init__(*args, **kw)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['last_name'].initial = self.instance.user.last_name
        self.fields['email'].initial = self.instance.user.email

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'location', 'birth_date', 'gender', 'website', 'bio')

    def save(self, user=None, **kwargs):
        user_profile = super(UserProfileForm, self).save(commit=False)
        if user:
            user_profile.user = user
        self.instance.user.first_name = self.cleaned_data.get('first_name')
        self.instance.user.last_name = self.cleaned_data.get('last_name')
        self.instance.user.email = self.cleaned_data.get('email')
        self.instance.user.save()
        user_profile.save()
        return user_profile
