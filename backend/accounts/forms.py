from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
import re


User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'college',
            'enrollment_number',
            'email',
            'username',
            'password1',
            'password2',
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_enrollment_number(self):
        value = (self.cleaned_data.get('enrollment_number') or '').strip()
        if not value:
            raise forms.ValidationError('Enrollment number is required.')

        if value.startswith('-'):
            raise forms.ValidationError('Enrollment number cannot be negative.')

        if '-' in value:
            raise forms.ValidationError('Minus sign is not allowed in enrollment number.')

        if not re.fullmatch(r'[A-Za-z0-9_]{4,50}', value):
            raise forms.ValidationError('Enrollment number must be 4-50 characters and use only letters, numbers, or _.')

        return value


class ResumeLoginForm(AuthenticationForm):
    resume_file = forms.FileField(
        required=True,
        help_text='Upload resume at login so technical questions can be pre-generated.',
    )
