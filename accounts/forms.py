from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser, Address


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
            'placeholder': 'Minimum 8 characters'
        }),
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
            'placeholder': 'Repeat your password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
                'placeholder': 'name@example.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
                'placeholder': 'Last Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
                'placeholder': '+250 788 000 000'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = CustomUser.ROLE_CUSTOMER  # Strictly force Customer role on public registration
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class CustomerLoginForm(forms.Form):
    email = forms.EmailInput()
    email = forms.CharField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm',
            'placeholder': '••••••••'
        })
    )


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone_number', 'street_address', 'city_district', 'province', 'country', 'delivery_instructions', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Full Contact Name'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': '+250 788 123 456'}),
            'street_address': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'House / Building / Street Number'}),
            'city_district': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'e.g. Nyarugenge, Gasabo, Kicukiro, Rubavu, Musanze'}),
            'province': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'e.g. Kigali City, Western Province'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'placeholder': 'Rwanda'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-lg border border-slate-300 text-sm', 'rows': 2, 'placeholder': 'Landmarks or specific instructions for delivery rider'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 rounded border-slate-300'}),
        }
