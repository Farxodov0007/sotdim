from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FreelanceProject, Proposal
from apps.orders.models import Order
import decimal

class FreelanceProjectListView(ListView):
    model = FreelanceProject
    template_name = "freelance/project_list.html"
    context_object_name = "projects"

@login_required
def create_freelance_order(request, project_id):
    """
    Submits a simple order/proposal for a freelance project.
    """
    project = get_object_or_404(FreelanceProject, id=project_id)
    
    if request.user == project.client:
        messages.error(request, "O'z loyihangizga buyurtma berolmaysiz!")
        return redirect('freelance:project_list')

    # Create a proposal automatically for demo
    Proposal.objects.get_or_create(
        project=project,
        freelancer=request.user,
        defaults={
            'cover_letter': "Men bu loyihani bajarishga tayyorman!",
            'bid_amount': project.budget,
            'delivery_days': 7
        }
    )

    # In a real app, the client would accept the proposal first.
    # For this demo, we create the Order immediately.
    order = Order.objects.create(
        buyer=project.client,
        freelancer=request.user,
        amount=project.budget,
        commission=project.budget * decimal.Decimal('0.15'),
        status='PENDING'
    )

    messages.success(request, "Buyurtma muvaffaqiyatli qabul qilindi!")
    return redirect('marketplace:order_confirm', order_id=order.id)
