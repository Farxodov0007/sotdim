from django.db import models
from django.conf import settings
from apps.marketplace.models import Product

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "To'lov kutilmoqda"
        AWAITING_APPROVAL = "AWAITING_APPROVAL", "Tasdiqlash kutilmoqda"
        PAID = "PAID", "To'lov qabul qilindi"
        IN_PROGRESS = "IN_PROGRESS", "Jarayonda"
        DELIVERED = "DELIVERED", "Yetkazildi"
        COMPLETED = "COMPLETED", "Yakunlandi"
        CANCELLED = "CANCELLED", "Bekor qilindi"
        REFUNDED = "REFUNDED", "Qaytarildi"

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="freelance_orders")
    coupon = models.ForeignKey('payments.Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    receipt_image = models.ImageField(upload_to="receipts/%Y/%m/%d/", blank=True, null=True, verbose_name="To'lov cheki")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"

    def save(self, *args, **kwargs):
        is_approval = False
        if self.pk:
            old_order = Order.objects.get(pk=self.pk)
            # Agar oldin PENDING yoki AWAITING bo'lib, endi PAID yoki COMPLETED bo'lsa:
            if old_order.status in [self.Status.PENDING, self.Status.AWAITING_APPROVAL] and self.status in [self.Status.PAID, self.Status.COMPLETED]:
                is_approval = True
        
        super().save(*args, **kwargs)

        if is_approval:
            from apps.payments.models import EscrowAccount
            from apps.notifications.models import Notification
            from django.db import transaction
            from decimal import Decimal
            from apps.core.utils import format_uzs

            with transaction.atomic():
                seller = self.product.seller if self.product else self.freelancer
                if seller:
                    wallet, _ = EscrowAccount.objects.get_or_create(user=seller)
                    net_amount = self.amount - self.commission
                    wallet.balance = Decimal(str(wallet.balance)) + net_amount
                    wallet.save()
                    
                    if self.product:
                        self.product.sales_count += 1
                        self.product.save()

                    Notification.objects.create(
                        user=seller,
                        notif_type='ORDER_PAID',
                        title="To'lov muvaffaqiyatli o'tdi!",
                        message=f"{self.buyer.username} dan {format_uzs(self.amount)} to'lov tasdiqlandi. Balansga +{format_uzs(net_amount)} qo'shildi."
                    )

                    # Notify buyer about the file download
                    Notification.objects.create(
                        user=self.buyer,
                        notif_type='ORDER_PAID',
                        title="Sotib olingan mahsulot tayyor!",
                        message=f"'{self.product.title if self.product else 'Loyiha'}' uchun to'lov tasdiqlandi! Endi uni Haridlarim bo'limidan yuklab olishingiz mumkin."
                    )

class Subscription(models.Model):
    class Plan(models.TextChoices):
        FREE = "FREE", "Free"
        BASIC = "BASIC", "Basic"
        PRO = "PRO", "Pro"
        PREMIUM = "PREMIUM", "Premium"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_subscription")
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Obuna"
        verbose_name_plural = "Obunalar"

    def __str__(self):
        return f"{self.user.username} - {self.plan}"
