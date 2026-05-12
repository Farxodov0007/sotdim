from django.contrib import admin
from django.utils.html import format_html
from .models import Order, Subscription
from apps.payments.models import EscrowAccount

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'amount', 'status', 'created_at', 'receipt_preview')
    list_filter = ('status',)
    actions = ['approve_orders']

    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-height: 50px;"/></a>', obj.receipt_image.url)
        return "-"
    receipt_preview.short_description = "Chek rasmi"

    @admin.action(description="Tanlangan tasdiq kutayotgan (chek yuklangan) buyurtmalarni tasdiqlash")
    def approve_orders(self, request, queryset):
        for order in queryset.filter(status='AWAITING_APPROVAL'):
            order.status = 'PAID'
            order.save()
        self.message_user(request, "Buyurtmalar tasdiqlandi va mablag'lar o'tkazildi.")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'expires_at')
