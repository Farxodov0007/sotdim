from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.urls import reverse
from .forms import CustomUserCreationForm, SellerOnboardingForm, SellerReferralForm
from django.contrib import messages
from .models import Follow, User, SellerProfile, SellerReferral, SellerVerification
from apps.payments.models import EscrowAccount
from apps.analytics.models import SellerAnalytics
from apps.marketplace.models import Product
from apps.orders.models import Order
from django.contrib.sites.shortcuts import get_current_site
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.decorators import login_required


def _social_app_enabled(request, provider_name: str) -> bool:
    try:
        current_site = get_current_site(request)
    except Exception:
        return False
    return SocialApp.objects.filter(provider=provider_name, sites__id=current_site.id).exists()


def login_view(request):
    google_login_enabled = _social_app_enabled(request, 'google')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.username}!")
                return redirect('core:dashboard')
        else:
            messages.error(request, "Login yoki parol noto'g'ri.")
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form, "google_login_enabled": google_login_enabled})

def register_view(request):
    google_login_enabled = _social_app_enabled(request, 'google')
    referral_code = request.GET.get('ref') or request.POST.get('referral_code')

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if referral_code:
                referral = SellerReferral.objects.filter(code=referral_code, is_converted=False).first()
                if referral:
                    referral.is_converted = True
                    referral.converted_at = timezone.now()
                    referral.save()
                    wallet, _ = EscrowAccount.objects.get_or_create(user=referral.referrer)
                    wallet.balance += 15000
                    wallet.save()
                    messages.success(request, "Referral bonusingiz muvaffaqiyatli qo'llandi!")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('core:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {
        "form": form,
        "google_login_enabled": google_login_enabled,
        "referral_code": referral_code,
    })

def become_seller(request):
    if request.user.is_authenticated and request.user.role == User.Role.SELLER:
        return redirect('users:seller_dashboard')

    return render(request, 'users/become_seller.html', {
        'google_login_enabled': _social_app_enabled(request, 'google')
    })

@login_required
def seller_onboarding(request):
    if request.user.role == User.Role.SELLER:
        return redirect('users:seller_dashboard')

    profile, _ = SellerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SellerOnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            seller_profile = form.save(commit=False)
            seller_profile.user = request.user
            seller_profile.verification_status = SellerProfile.VerificationStatus.PENDING
            seller_profile.save()
            SellerVerification.objects.get_or_create(profile=seller_profile, defaults={
                'status': SellerVerification.Status.PENDING
            })
            request.user.role = User.Role.SELLER
            request.user.save(update_fields=['role'])
            messages.success(request, "Sotuvchi bo'lishingiz uchun arizangiz qabul qilindi. Bizning jamoamiz uni ko'rib chiqadi.")
            return redirect('users:seller_dashboard')
    else:
        form = SellerOnboardingForm(instance=profile)

    return render(request, 'users/seller_onboarding.html', {
        'form': form,
        'profile': profile,
    })

@login_required
def seller_dashboard(request):
    if request.user.role != User.Role.SELLER:
        return redirect('users:become_seller')

    profile, _ = SellerProfile.objects.get_or_create(user=request.user)
    verification = getattr(profile, 'verification', None)
    wallet, _ = EscrowAccount.objects.get_or_create(user=request.user)
    referrals = SellerReferral.objects.filter(referrer=request.user).order_by('-created_at')
    analytics = SellerAnalytics.objects.filter(seller=request.user).order_by('-date')[:6]
    recent_sales = Order.objects.filter(product__seller=request.user, status='PAID').order_by('-created_at')[:5]
    top_products = Product.objects.filter(seller=request.user).order_by('-view_count')[:5]
    referral_url = request.build_absolute_uri(reverse('users:register')) + f"?ref={profile.referral_code}"
    referral_form = SellerReferralForm()

    return render(request, 'users/seller_dashboard.html', {
        'profile': profile,
        'verification': verification,
        'wallet': wallet,
        'analytics': analytics,
        'recent_sales': recent_sales,
        'top_products': top_products,
        'referral_url': referral_url,
        'referral_form': referral_form,
        'referrals': referrals,
    })

@login_required
def submit_referral(request):
    if request.user.role != User.Role.SELLER:
        return redirect('users:become_seller')

    if request.method == 'POST':
        form = SellerReferralForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.referrer = request.user
            referral.commission = 15000
            referral.save()
            messages.success(request, "Referal taklifingiz muvaffaqiyatli saqlandi. Foydalanuvchi ro'yxatdan o'tganda sizga ballar beriladi.")
        else:
            messages.error(request, "Iltimos, haqiqiy elektron pochta manzilini kiriting.")

    return redirect('users:seller_dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect('users:login')

@login_required
def toggle_follow(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return redirect(request.META.get('HTTP_REFERER', 'marketplace:product_list'))
        
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target_user)
    if not created:
        follow.delete()
        messages.info(request, f"{target_user.username} kuzatishni to'xtatdingiz.")
    else:
        messages.success(request, f"{target_user.username} kuzatishni boshladingiz.")
        
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:product_list'))
