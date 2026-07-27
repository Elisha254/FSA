from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class AccountCreateForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '+254700000000'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        return email

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role:
            return 'intern'
        return role
