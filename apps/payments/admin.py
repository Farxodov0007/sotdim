from django.contrib import admin
from .models import EscrowAccount, Transaction, WithdrawalRequest, CompanyCard, Coupon, CouponUsage, CouponValidationAttempt

@admin.register(EscrowAccount)
class EscrowAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'frozen_balance')

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['approve_withdrawals']

    @admin.action(description="Tanlangan so'rovlarni tasdiqlash va balansdan chegirish")
    def approve_withdrawals(self, request, queryset):
        from decimal import Decimal
        for req in queryset.filter(status='PENDING'):
            wallet = EscrowAccount.objects.get(user=req.user)
            balance = Decimal(str(wallet.balance))
            if balance >= req.amount:
                wallet.balance = balance - req.amount
                wallet.save()
                req.status = 'APPROVED'
                req.save()
            else:
                self.message_user(request, f"{req.user.username} balansida mablag' yetarli emas!", level='error')
        self.message_user(request, "So'rovlar tasdiqlandi va mablag'lar yechildi.")

admin.site.register(Transaction)

@admin.register(CompanyCard)
class CompanyCardAdmin(admin.ModelAdmin):
    list_display = ('card_name', 'card_number', 'card_holder', 'is_active')
    list_filter = ('is_active', 'card_name')
    search_fields = ('card_number', 'card_holder')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_until')
    list_filter = ('is_active', 'discount_type', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Chegirma', {
            'fields': ('discount_type', 'discount_value', 'max_discount')
        }),
        ('Cheklovlar', {
            'fields': (
                'minimum_amount', 'usage_limit', 'per_user_limit',
                'valid_from', 'valid_until',
                'allowed_categories', 'allowed_sellers'
            )
        }),
        ('Qo\'shimcha', {
            'fields': ('is_new_user_only', 'is_premium_only', 'apply_to_marketplace', 'apply_to_subscription'),
        }),
        ('Sana', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'amount_saved', 'created_at')
    list_filter = ('coupon', 'created_at')
    search_fields = ('user__username', 'coupon__code')
    readonly_fields = ('coupon', 'user', 'order', 'amount_saved', 'ip_address', 'created_at')


@admin.register(CouponValidationAttempt)
class CouponValidationAttemptAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'is_success', 'created_at')
    list_filter = ('is_success', 'created_at')
    search_fields = ('code', 'user__username')
    readonly_fields = ('coupon', 'user', 'order', 'code', 'ip_address', 'reason', 'created_at')
