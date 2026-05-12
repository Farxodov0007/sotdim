from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserActivity, SellerProfile, SellerVerification, SellerReferral
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("email", "username", "role", "badge", "is_verified", "is_staff")
    list_filter = ("role", "badge", "is_verified", "is_staff", "is_superuser")
    search_fields = ("email", "username")
    ordering = ("email",)
    fieldsets = UserAdmin.fieldsets + (
        ("Profil", {"fields": ("role", "badge", "phone_number", "telegram_id", "avatar", "bio", "is_verified", "two_factor_enabled")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role", "phone_number", "is_staff", "is_superuser"),
        }),
    )

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "ip_address", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("user__email", "action")


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "verification_status", "rating", "total_sales", "total_revenue", "referral_code", "created_at")
    list_filter = ("verification_status", "is_top_seller", "created_at")
    search_fields = ("user__email", "user__username", "referral_code")


@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    list_display = ("profile", "status", "phone_verified", "telegram_verified", "requested_at", "reviewed_at")
    list_filter = ("status", "phone_verified", "telegram_verified")
    search_fields = ("profile__user__email", "profile__user__username")


@admin.register(SellerReferral)
class SellerReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_email", "code", "commission", "is_converted", "created_at", "converted_at")
    list_filter = ("is_converted", "created_at")
    search_fields = ("referrer__email", "referred_email", "code")
