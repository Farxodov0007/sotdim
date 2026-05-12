from django.urls import path
from .views import (
    login_view,
    register_view,
    logout_view,
    toggle_follow,
    become_seller,
    seller_onboarding,
    seller_dashboard,
    submit_referral,
)

app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("become-seller/", become_seller, name="become_seller"),
    path("seller/onboard/", seller_onboarding, name="seller_onboarding"),
    path("seller/dashboard/", seller_dashboard, name="seller_dashboard"),
    path("seller/referral/", submit_referral, name="submit_referral"),
    path("follow/<int:user_id>/", toggle_follow, name="toggle_follow"),
]
