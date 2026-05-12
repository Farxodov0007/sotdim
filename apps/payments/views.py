from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import EscrowAccount, WithdrawalRequest, UserCard
from apps.core.utils import format_uzs
import decimal

class WalletView(TemplateView):
    template_name = "payments/wallet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            wallet, _ = EscrowAccount.objects.get_or_create(user=self.request.user)
            context['wallet'] = wallet
            context['withdrawals'] = WithdrawalRequest.objects.filter(user=self.request.user).order_by('-created_at')
            context['cards'] = UserCard.objects.filter(user=self.request.user)
        return context

@login_required
def add_card(request):
    if request.method == "POST":
        card_number = request.POST.get('card_number')
        card_holder = request.POST.get('card_holder')
        expiry_date = request.POST.get('expiry_date')
        
        if card_number and card_holder:
            UserCard.objects.create(
                user=request.user,
                card_number=card_number,
                card_holder=card_holder,
                expiry_date=expiry_date
            )
            messages.success(request, "Yangi karta muvaffaqiyatli qo'shildi!")
        else:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring.")
            
    return redirect('payments:wallet')

@login_required
def withdraw_funds(request):
    if request.method == "POST":
        amount_str = request.POST.get('amount', '').strip()
        card_id = request.POST.get('card_id')
        
        if not amount_str:
            messages.error(request, "Iltimos, summani kiriting.")
            return redirect('payments:wallet')

        try:
            amount = decimal.Decimal(amount_str)
        except decimal.InvalidOperation:
            messages.error(request, "Noto'g'ri summa.")
            return redirect('payments:wallet')

        wallet, _ = EscrowAccount.objects.get_or_create(user=request.user)
        
        if wallet.balance < amount:
            messages.error(request, "Hisobda mablag' yetarli emas.")
        else:
            card = UserCard.objects.filter(id=card_id, user=request.user).first()
            WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                card=card,
                status='PENDING'
            )
            messages.info(request, f"{format_uzs(amount)} yechib olish uchun so'rov yuborildi.")
            
    return redirect('payments:wallet')
