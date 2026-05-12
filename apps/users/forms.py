from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, SellerProfile, SellerReferral

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        label="Telefon raqami",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone_number")
    
    field_order = ["username", "email", "phone_number", "password1", "password2"]

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "role",
            "phone_number",
            "telegram_id",
            "avatar",
            "bio",
            "is_verified",
            "two_factor_enabled",
            "is_staff",
            "is_superuser",
            "is_active",
        )


class SellerOnboardingForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Sotuvchi haqida qisqacha yozing...',
            'class': 'w-full rounded-3xl border border-slate-800/70 bg-slate-900 px-4 py-4 text-white placeholder:text-slate-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none'
        }),
        label="Qisqacha bio"
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Masalan: UX dizayn, marketing, SEO',
            'class': 'w-full rounded-3xl border border-slate-800/70 bg-slate-900 px-4 py-4 text-white placeholder:text-slate-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none'
        }),
        label="Ko'nikmalar"
    )
    portfolio_links = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'https://portfolio.example.com, https://github.com/username',
            'class': 'w-full rounded-3xl border border-slate-800/70 bg-slate-900 px-4 py-4 text-white placeholder:text-slate-500 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none'
        }),
        help_text="Portfoliongizni vergul bilan ajrating.",
        label="Portfolio havolalari"
    )

    class Meta:
        model = SellerProfile
        fields = ["bio", "skills", "portfolio_links"]

    def clean_portfolio_links(self):
        value = self.cleaned_data.get("portfolio_links", "")
        if value:
            links = [link.strip() for link in value.split(",") if link.strip()]
            return links
        return []


class SellerReferralForm(forms.ModelForm):
    class Meta:
        model = SellerReferral
        fields = ["referred_email"]
        widgets = {
            "referred_email": forms.EmailInput(attrs={
                'placeholder': 'friend@example.com'
            }),
        }
