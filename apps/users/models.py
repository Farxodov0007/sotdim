import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_referral_code():
    return uuid.uuid4().hex[:10].upper()

class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", _("User")
        SELLER = "SELLER", _("Seller")
        FREELANCER = "FREELANCER", _("Freelancer")
        MODERATOR = "MODERATOR", _("Moderator")
        SUPPORT = "SUPPORT", _("Support")
        ADMIN = "ADMIN", _("Admin")

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(_("telefon raqami"), max_length=20, blank=True, null=True)
    telegram_id = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    @property
    def is_seller(self):
        return self.role == self.Role.SELLER

    def get_seller_profile(self):
        profile, _ = SellerProfile.objects.get_or_create(user=self)
        return profile
    
    # Seller Badge System
    class BadgeLevel(models.TextChoices):
        NONE = "NONE", "Oddiy"
        VERIFIED = "VERIFIED", "Tasdiqlangan ✓"
        PREMIUM = "PREMIUM", "Premium ⭐"
        TRUSTED = "TRUSTED", "Ishonchli 🛡️"
        TOP_SELLER = "TOP_SELLER", "Top Seller 🏆"

    badge = models.CharField(max_length=20, choices=BadgeLevel.choices, default=BadgeLevel.NONE)
    
    is_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    has_saved_card = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-created_at']

    def __str__(self):
        return self.email

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foydalanuvchi faoliyati"
        verbose_name_plural = "Foydalanuvchilar faoliyati"
        ordering = ['-timestamp']


class SellerProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "UNVERIFIED", "Unverified"
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller_profile")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    bio = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)
    portfolio_links = models.JSONField(blank=True, null=True, default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sales = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    trust_score = models.PositiveSmallIntegerField(default=65)
    followers_count = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.UNVERIFIED)
    referral_code = models.CharField(max_length=20, unique=True, default=generate_referral_code)
    is_top_seller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seller profili"
        verbose_name_plural = "Seller profillari"

    def __str__(self):
        return f"{self.user.email} - {self.user.role}"


class SellerVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    profile = models.OneToOneField(SellerProfile, on_delete=models.CASCADE, related_name="verification")
    phone_verified = models.BooleanField(default=False)
    telegram_verified = models.BooleanField(default=False)
    identity_document = models.FileField(upload_to="seller_verification/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    review_notes = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Seller tasdiqlash"
        verbose_name_plural = "Seller tasdiqlashlari"

    def __str__(self):
        return f"{self.profile.user.email} - {self.status}"


class SellerReferral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_referrals')
    referred_email = models.EmailField()
    code = models.CharField(max_length=20, unique=True, default=generate_referral_code)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Seller referral"
        verbose_name_plural = "Seller referral'lari"

    def __str__(self):
        return f"{self.referrer.email} → {self.referred_email}"


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = "Kuzatuv"
        verbose_name_plural = "Kuzatuvlar"

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
