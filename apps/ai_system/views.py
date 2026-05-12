from django.views.generic import TemplateView
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from apps.marketplace.models import Product
from apps.core.utils import format_uzs
import decimal

class AIAssistantView(TemplateView):
    template_name = "ai_system/assistant.html"

def apply_ai_recommendation(request):
    """
    Simulates applying an AI recommendation (e.g., updating a product price).
    """
    if request.method == "POST":
        product = Product.objects.filter(seller=request.user).first()
        if product:
            old_price = product.price
            product.price = product.price * decimal.Decimal('1.15')
            product.save()
            return JsonResponse({
                "status": "success", 
                "message": f"'{product.title}' narxi {format_uzs(old_price)} dan {format_uzs(product.price)} ga optimallashtirildi!"
            })
    return JsonResponse({"status": "error", "message": "Xatolik yuz berdi"}, status=400)

def ai_chat_view(request):
    """
    Handles AI chat messages using HTMX.
    """
    if request.method == "POST":
        user_message = request.POST.get('message', '').lower()
        
        # Simple AI Logic (Replace with OpenAI/Gemini later)
        if "salom" in user_message:
            response = "Salom! Men sizning biznes yordamchingizman. Qanday yordam bera olaman?"
        elif "narx" in user_message:
            response = "AI tahlili bo'yicha mahsulotlaringiz narxi bozorga mos. Sotuvlarni oshirish uchun tavsifni boyitishni maslahat beraman."
        elif "trend" in user_message:
            response = "Hozirda AI Promptlar va SaaS shablonlari eng ko'p sotilayotgan mahsulotlar qatorida."
        else:
            response = f"Tushunarlu. '{user_message}' bo'yicha tahlil o'tkazyapman. Bu borada yangi trendlarni o'rganishni tavsiya qilaman."

        import time
        # time.sleep(0.5) # Simulate thinking

        return render(request, 'ai_system/partials/chat_message.html', {
            'message': response,
            'user_message': request.POST.get('message')
        })
    return HttpResponse("Faqat POST so'rovlari ruxsat etilgan", status=400)
