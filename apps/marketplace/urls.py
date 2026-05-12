from django.urls import path
from .views import (
    ProductListView, ProductCreateView,
    download_report, create_order,
    category_detail, product_detail, product_list_partial,
    order_confirm, payment_page, apply_coupon_ajax,
    toggle_wishlist, wishlist_view,
    ai_smart_search_view, ai_generate_seo, one_click_buy
)

app_name = "marketplace"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("create/", ProductCreateView.as_view(), name="product_create"),
    path("report/", download_report, name="download_report"),
    path("buy/<int:product_id>/", create_order, name="create_order"),
    path("category/<slug:slug>/", category_detail, name="category_detail"),
    path("product/<slug:slug>/", product_detail, name="product_detail"),
    path("order/confirm/<int:order_id>/", order_confirm, name="order_confirm"),
    path("order/pay/<int:order_id>/", payment_page, name="payment_page"),
    path("order/apply_coupon/<int:order_id>/", apply_coupon_ajax, name="apply_coupon"),
    path("search/", product_list_partial, name="product_list_partial"),
    
    # Wishlist
    path("wishlist/", wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),
    
    # AI Features
    path("ai-search/", ai_smart_search_view, name="ai_smart_search"),
    path("ai-seo/", ai_generate_seo, name="ai_generate_seo"),
    
    # One-click Buy
    path("buy-now/<int:product_id>/", one_click_buy, name="one_click_buy"),
]
