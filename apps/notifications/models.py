from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER_NEW = "ORDER_NEW", "Yangi buyurtma"
        ORDER_PAID = "ORDER_PAID", "To'lov tasdiqlandi"
        ORDER_CANCELLED = "ORDER_CANCELLED", "Buyurtma bekor qilindi"
        WITHDRAWAL_APPROVED = "WITHDRAWAL_APPROVED", "Yechib olish tasdiqlandi"
        WITHDRAWAL_REJECTED = "WITHDRAWAL_REJECTED", "Yechib olish rad etildi"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
