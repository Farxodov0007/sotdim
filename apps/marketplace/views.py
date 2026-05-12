import json
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import csv
import decimal
from .models import Product, Category, Subcategory
from apps.orders.models import Order
from apps.core.utils import format_uzs
from apps.payments.services import validate_coupon_for_order, apply_coupon_to_order, register_coupon_usage
from apps.freelance.models import FreelanceProject
from apps.users.models import User
from django.db.models import Count, F

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['title', 'category', 'subcategory', 'product_type', 'price', 'sale_price', 'preview_image', 'demo_url', 'tags', 'description']
    template_name = "marketplace/product_form.html"
    success_url = reverse_lazy('marketplace:product_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role != User.Role.SELLER:
            messages.warning(request, "Seller bo'lishingiz kerak, mahsulot qo'shish uchun.")
            return redirect('users:become_seller')
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        selected_category = None
        if self.request.method == 'POST':
            category_id = self.request.POST.get('category')
            selected_category = Category.objects.filter(id=category_id).first()

        if selected_category:
            form.fields['subcategory'].queryset = Subcategory.objects.filter(category=selected_category)
        else:
            form.fields['subcategory'].queryset = Subcategory.objects.all()

        form.fields['subcategory'].widget.attrs.update({
            'data-category-field': 'category'
        })
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subcategories = Subcategory.objects.all()
        context['subcategories'] = subcategories
        context['subcategories_json'] = json.dumps([
            {
                'id': sub.id,
                'name': sub.name,
                'category_id': sub.category_id,
            }
            for sub in subcategories
        ])
        return context

    def form_valid(self, form):
        product_file = self.request.FILES.get('product_file')
        if not product_file:
            messages.error(self.request, "Iltimos, mahsulot faylini ham yuklang!")
            return self.form_invalid(form)
            
        form.instance.seller = self.request.user
        response = super().form_valid(form)
        
        # Mahsulot asosi saqlangach, fayl modelini yaratamiz
        from .models import ProductFile
        ProductFile.objects.create(
            product=self.object,
            file=product_file,
            version="1.0.0"
        )
        
        messages.success(self.request, "Mahsulot muvaffaqiyatli qo'shildi va fayl yuklandi!")
        return response

def download_report(request):
    """
    Generates a simple CSV report of sales.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="hisobot.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Mahsulot', 'Sotuvchi', 'Narx', 'Sana'])
    
    products = Product.objects.all()
    for p in products:
        writer.writerow([p.title, p.seller.username, p.price, p.created_at])
        
    return response

from django.contrib.auth.decorators import login_required
from django.db.models import F

@login_required
def create_order(request, product_id):
    """
    Creates an order for a product.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.user == product.seller:
        messages.error(request, "O'z mahsulotingizni sotib ololmaysiz!")
        return redirect('marketplace:product_list')
        
    # Create Order in PENDING status
    order = Order.objects.create(
        buyer=request.user,
        product=product,
        amount=product.price,
        final_amount=product.price,
        discount_amount=decimal.Decimal('0.00'),
        coupon_code=None,
        commission=product.price * decimal.Decimal('0.1'),
        status='PENDING'
    )
    
    # Sotuvchiga bildirishnoma yuborish
    from apps.notifications.models import Notification
    Notification.objects.create(
        user=product.seller,
        notif_type='ORDER_NEW',
        title='Yangi buyurtma keldi!',
        message=f"{request.user.username} sizning '{product.title}' mahsulotingizga buyurtma berdi. Summa: {format_uzs(product.price)}"
    )

    messages.success(request, "Buyurtma qabul qilindi! To'lovni amalga oshiring.")
    return redirect('marketplace:payment_page', order_id=order.id)

@login_required
def order_confirm(request, order_id):
    from apps.orders.models import Order
    from django.db.models import Q
    # Xaridor ham, sotuvchi ham ko'ra olishi uchun Q dan foydalanamiz
    order = get_object_or_404(Order, Q(buyer=request.user) | Q(freelancer=request.user) | Q(product__seller=request.user), id=order_id)
    return render(request, 'marketplace/order_confirm.html', {'order': order})

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.filter(is_active=True).select_related('category', 'seller', 'subcategory'), slug=slug)
    Product.objects.filter(pk=product.pk).update(view_count=F('view_count') + 1)
    product.refresh_from_db(fields=['view_count'])

    followed_seller_ids = []
    if request.user.is_authenticated:
        followed_seller_ids = list(request.user.following.values_list('following_id', flat=True))

    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'followed_seller_ids': followed_seller_ids,
    })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).select_related('seller', 'subcategory')
    popular_sellers = User.objects.filter(
        products__category=category,
        products__is_active=True
    ).annotate(product_count=Count('products')).order_by('-product_count').distinct()[:8]
    freelance_projects = FreelanceProject.objects.filter(category=category).order_by('-created_at')[:6]
    subcategories = category.subcategories.all()

    followed_seller_ids = []
    if request.user.is_authenticated:
        followed_seller_ids = list(request.user.following.values_list('following_id', flat=True))

    return render(request, 'marketplace/category_detail.html', {
        'category': category,
        'products': products,
        'popular_sellers': popular_sellers,
        'freelance_projects': freelance_projects,
        'subcategories': subcategories,
        'followed_seller_ids': followed_seller_ids,
    })

@login_required
def apply_coupon_ajax(request, order_id):
    """
    AJAX endpoint to validate and apply a coupon code to an order.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=400)

    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    coupon_code = request.POST.get('coupon_code', '').strip()

    try:
        result = validate_coupon_for_order(order, coupon_code, request)
        
        # Apply the coupon to the order
        apply_coupon_to_order(
            order,
            result['coupon'],
            result['discount_amount'],
            result['final_amount'],
            result['commission']
        )

        return JsonResponse({
            'success': True,
            'message': result['message'],
            'discount_amount': str(result['discount_amount']),
            'final_amount': str(result['final_amount']),
            'discount_display': format_uzs(result['discount_amount']),
            'final_display': format_uzs(result['final_amount']),
        })
    except ValidationError as exc:
        return JsonResponse({
            'success': False,
            'message': str(exc.message) if hasattr(exc, 'message') else str(exc),
        }, status=400)
    except Exception as exc:
        return JsonResponse({
            'success': False,
            'message': 'Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.',
        }, status=500)


@login_required
def payment_page(request, order_id):
    """
    Payment page: user sees the order and clicks 'Pay' button.
    User specifies the payment method, chooses a company card, details are shown.
    User pays and uploads receipt_image. Order status becomes AWAITING_APPROVAL.
    """
    from apps.orders.models import Order
    from apps.payments.models import CompanyCard, EscrowAccount
    from django.db.models import Q

    order = get_object_or_404(Order, Q(buyer=request.user) | Q(freelancer=request.user) | Q(product__seller=request.user), id=order_id)

    wallet, _ = EscrowAccount.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if order.buyer != request.user:
            messages.error(request, "Faqat xaridor to'lov qila oladi!")
            return redirect('marketplace:order_confirm', order_id=order.id)
            
        if 'pay_from_balance' in request.POST:
            if wallet.balance >= order.final_amount:
                # Deduct from user wallet using final_amount (with discount applied)
                from decimal import Decimal
                wallet.balance = Decimal(str(wallet.balance)) - order.final_amount
                wallet.save()
                
                order.status = 'PAID'
                order.payment_method = 'Shaxsiy hisob (Escrow)'
                order.save()
                
                # Register coupon usage if applied
                if order.coupon:
                    register_coupon_usage(
                        order,
                        request.user,
                        order.discount_amount,
                        request=request
                    )
                
                messages.success(request, "To'lov shaxsiy hisobingizdan muvaffaqiyatli amalga oshirildi!")
                return redirect('marketplace:order_confirm', order_id=order.id)
            else:
                messages.error(request, "Hisobingizda mablag' yetarli emas!")
                return redirect('marketplace:payment_page', order_id=order.id)

        receipt = request.FILES.get('receipt_image')
        if not receipt:
            messages.error(request, "Iltimos, to'lov cheki rasmini yuklang!")
            return redirect('marketplace:payment_page', order_id=order.id)

        # Update order status to AWAITING_APPROVAL using final_amount
        order.status = 'AWAITING_APPROVAL'
        order.payment_method = request.POST.get('payment_method', 'Karta orqali')
        order.receipt_image = receipt
        order.save()
        
        # Register coupon usage if applied
        if order.coupon:
            register_coupon_usage(
                order,
                request.user,
                order.discount_amount,
                request=request
            )

        messages.success(request, "To'lov cheki yuklandi! Admin tasdiqlashi kutilmoqda.")
        return redirect('marketplace:order_confirm', order_id=order.id)

    company_cards = CompanyCard.objects.filter(is_active=True)
    return render(request, 'marketplace/payment_page.html', {
        'order': order,
        'company_cards': company_cards,
        'wallet': wallet
    })

class ProductListView(ListView):
    model = Product
    template_name = "marketplace/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'subcategory', 'seller')
        q = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        subcategory_slug = self.request.GET.get('subcategory')
        
        if q:
            queryset = queryset.filter(title__icontains=q)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
            
        return queryset

    def get_context_data(self, **kwargs):
        if Category.objects.count() == 0:
            Category.seed_default_categories()

        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')
        context['subcategories'] = Subcategory.objects.all()
        context['top_viewed_products'] = Product.objects.filter(is_active=True).order_by('-view_count')[:4]
        if self.request.user.is_authenticated:
            context['followed_seller_ids'] = list(self.request.user.following.values_list('following_id', flat=True))
        return context

def product_list_partial(request):
    """
    HTMX partial view for product filtering/search.
    """
    q = request.GET.get('q')
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    
    products = Product.objects.filter(is_active=True)
    if q:
        products = products.filter(title__icontains=q)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
        
    context = {'products': products}
    if request.user.is_authenticated:
        context['followed_seller_ids'] = list(request.user.following.values_list('following_id', flat=True))
    return render(request, 'marketplace/partials/product_grid.html', context)


@login_required
def toggle_wishlist(request, product_id):
    """Wishlist ga qo'shish yoki olib tashlash."""
    from .models import Wishlist
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        wishlist.delete()
        messages.info(request, f"'{product.title}' istaklar ro'yxatidan olib tashlandi.")
    else:
        messages.success(request, f"'{product.title}' istaklar ro'yxatiga qo'shildi!")
    return redirect(request.META.get('HTTP_REFERER', 'marketplace:product_list'))


@login_required
def wishlist_view(request):
    """Foydalanuvchining istaklar ro'yxati."""
    from .models import Wishlist
    wishlisted = Wishlist.objects.filter(user=request.user).select_related('product', 'product__seller', 'product__category')
    return render(request, 'marketplace/wishlist.html', {'wishlisted': wishlisted})


@login_required
def ai_smart_search_view(request):
    """AI Smart Search - aqlli qidiruv."""
    query = request.GET.get('ai_q', '').strip()
    results = []
    ai_suggestion = None

    if query:
        from apps.ai_system.services import ai_smart_search
        # Mavjud kategoriyalar konteksti
        categories = list(Category.objects.values_list('name', flat=True))
        context_str = f"Kategoriyalar: {', '.join(categories)}"
        ai_result = ai_smart_search(query, context_str)

        if ai_result and ai_result.get('keywords'):
            from django.db.models import Q
            q_filter = Q()
            for kw in ai_result['keywords']:
                q_filter |= Q(title__icontains=kw) | Q(description__icontains=kw) | Q(tags__icontains=kw)
            results = Product.objects.filter(q_filter, is_active=True).select_related('seller', 'category')[:20]
            ai_suggestion = ai_result.get('suggestion')

    return render(request, 'marketplace/ai_search.html', {
        'query': query,
        'results': results,
        'ai_suggestion': ai_suggestion,
    })


@login_required
def ai_generate_seo(request):
    """AJAX - AI Auto Title & SEO generator."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=400)

    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    product_type = request.POST.get('product_type', '')

    from apps.ai_system.services import ai_auto_seo
    result = ai_auto_seo(title, description, product_type)
    if result:
        return JsonResponse({'success': True, 'data': result})
    return JsonResponse({'success': False, 'message': 'AI xizmati javob bermadi.'})


@login_required
def one_click_buy(request, product_id):
    """Siz saqlagan karta orqali bir bosishda sotib olish."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if not request.user.has_saved_card:
        messages.warning(request, "Bir bosishda sotib olish uchun avval kartangizni saqlashingiz kerak.")
        return redirect('marketplace:product_detail', slug=product.slug)

    from decimal import Decimal
    order = Order.objects.create(
        buyer=request.user,
        product=product,
        amount=product.sale_price if product.sale_price else product.price,
        commission=(product.sale_price if product.sale_price else product.price) * Decimal('0.1'),
        final_amount=product.sale_price if product.sale_price else product.price,
        status='PAID',
        payment_method="Saved Card"
    )
    messages.success(request, f"'{product.title}' muvaffaqiyatli sotib olindi! (Saved Card)")
    return redirect('core:order_tracking', order_id=order.id)

