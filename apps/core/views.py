from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from apps.marketplace.models import Product, Category
from apps.orders.models import Order
from apps.payments.models import EscrowAccount
from apps.users.models import User
from django.db.models import Q, Count, Sum

class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            # Followed sellers
            context['followed_seller_ids'] = list(user.following.values_list('following_id', flat=True))
            
            # Product and order stats
            context['total_products'] = Product.objects.filter(seller=user).count()
            context['buyer_orders_count'] = Order.objects.filter(buyer=user).count()
            context['seller_orders_count'] = Order.objects.filter(product__seller=user, status='PAID').count()
            context['paid_income'] = Order.objects.filter(product__seller=user, status='PAID').aggregate(total=Sum('amount'))['total'] or 0
            context['buyer_spent'] = Order.objects.filter(buyer=user, status='PAID').aggregate(total=Sum('amount'))['total'] or 0
            
            wallet, _ = EscrowAccount.objects.get_or_create(user=user)
            context['balance'] = wallet.balance
            
            # Conversion rate based on product views
            total_views = Product.objects.filter(seller=user).aggregate(total=Sum('view_count'))['total'] or 0
            context['conversion_rate'] = round((context['seller_orders_count'] / total_views) * 100, 2) if total_views else 0
            context['total_views'] = total_views
            
            # Site-wide active users
            context['active_users'] = User.objects.filter(is_active=True).count()
            
            # Seed default category structure if missing
            if Category.objects.count() == 0:
                Category.seed_default_categories()

            # Homepage categories and trending categories
            context['categories'] = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')[:16]
            context['trending_categories'] = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')[:3]
            
            # Feed from followed sellers
            followed_seller_ids = user.following.values_list('following_id', flat=True)
            context['followed_products'] = Product.objects.filter(seller_id__in=followed_seller_ids).order_by('-created_at')[:8]
            
            # Highest-viewed product for the current user
            context['top_viewed_product'] = Product.objects.filter(seller=user, is_active=True).order_by('-view_count').first()
            
            # Recent Activities (Bought or Sold)
            context['recent_orders'] = Order.objects.filter(
                Q(buyer=user) | Q(product__seller=user) | Q(freelancer=user)
            ).distinct().order_by('-created_at')[:10]
            # AI Product Recommendations
            try:
                from apps.ai_system.services import ai_product_recommendation
                user_orders = list(Order.objects.filter(buyer=user).values_list('product__title', flat=True))
                recent_views = list(Product.objects.filter(is_active=True).order_by('-view_count')[:10].values('id', 'title'))
                
                user_history = f"Sotib olgan: {', '.join(user_orders)}. Oxirgi ko'rgan mahsulotlari soni: 10."
                available_context = "\n".join([f"ID: {p['id']}, Nomi: {p['title']}" for p in recent_views])
                
                ai_recs = ai_product_recommendation(user_history, available_context)
                if ai_recs:
                    rec_ids = [r['product_id'] for r in ai_recs if isinstance(r, dict) and 'product_id' in r]
                    context['ai_recommendations'] = Product.objects.filter(id__in=rec_ids, is_active=True).select_related('seller', 'category')
                    context['ai_reasons'] = {r['product_id']: r.get('reason', '') for r in ai_recs if isinstance(r, dict)}
            except Exception:
                pass

        return context

class PurchasesListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "core/purchases.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        # Oluvchi barcha buyurtmalarini ko'radi (to'lov kutilayotganlarni ham)
        return Order.objects.filter(
            buyer=self.request.user,
            product__isnull=False
        ).select_related('product', 'product__seller').order_by('-created_at')

@login_required
def order_tracking(request, order_id):
    """Buyurtmani kuzatish (Live Tracking)."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Tracking status flow
    statuses = [
        {'id': 'PENDING', 'label': "To'lov kutilmoqda", 'icon': 'credit-card'},
        {'id': 'AWAITING_APPROVAL', 'label': "Tasdiqlash kutilmoqda", 'icon': 'clock'},
        {'id': 'PAID', 'label': "To'lov qabul qilindi", 'icon': 'check-circle'},
        {'id': 'IN_PROGRESS', 'label': "Jarayonda", 'icon': 'refresh-cw'},
        {'id': 'DELIVERED', 'label': "Yetkazildi", 'icon': 'truck'},
        {'id': 'COMPLETED', 'label': "Yakunlandi", 'icon': 'package'},
    ]
    
    # Find current status index
    current_index = -1
    for i, s in enumerate(statuses):
        if s['id'] == order.status:
            current_index = i
            break
            
    return render(request, 'core/order_tracking.html', {
        'order': order,
        'statuses': statuses,
        'current_index': current_index
    })

@login_required
def download_purchase(request, order_id):
    # Buyurtma egasi aynan request usermi va holati PAID/COMPLETED ekanligini tekshiramiz
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    if order.status not in ['PAID', 'COMPLETED']:
        return HttpResponseForbidden("Sizda ushbu mahsulotni yuklab olish huquqi yo'q. To'lov tasdiqlanmagan.")
        
    product_file = order.product.files.first()
    if not product_file or not product_file.file:
        raise Http404("Fayl topilmadi yoki sotuvchi hali fayl yuklamagan.")
        
    # Faylni foydalanuvchiga taqdim etamiz
    try:
        response = FileResponse(product_file.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{product_file.file.name.split("/")[-1]}"'
        return response
    except Exception:
        raise Http404("Faylni o'qishda xatolik yuz berdi.")
