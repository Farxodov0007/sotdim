from django.urls import path
from .views import WalletView, withdraw_funds, add_card

app_name = "payments"

urlpatterns = [
    path("wallet/", WalletView.as_view(), name="wallet"),
    path("withdraw/", withdraw_funds, name="withdraw"),
    path("add-card/", add_card, name="add_card"),
]
