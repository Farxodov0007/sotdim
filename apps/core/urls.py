from django.urls import path
from .views import DashboardView, PurchasesListView, download_purchase, order_tracking

app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("purchases/", PurchasesListView.as_view(), name="purchases"),
    path("purchases/track/<int:order_id>/", order_tracking, name="order_tracking"),
    path("purchases/download/<int:order_id>/", download_purchase, name="download_purchase"),
]
