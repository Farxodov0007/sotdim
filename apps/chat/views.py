from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_list(request):
    conversations = request.user.conversations.all().order_by('-updated_at')
    # Har bir suhbat uchun suhbatdoshni aniqlab chiqamiz
    for conv in conversations:
        conv.recipient = conv.participants.exclude(id=request.user.id).first()
    return render(request, 'chat/chat_list.html', {'conversations': conversations})

@login_required
def chat_detail(request, conversation_id):
    conversation = get_object_or_404(request.user.conversations, id=conversation_id)
    messages = conversation.messages.all()
    # Mark messages as read
    conversation.messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    recipient = conversation.participants.exclude(id=request.user.id).first()
    
    # Sidebar uchun barcha suhbatlarni boyitish
    all_conversations = request.user.conversations.all().order_by('-updated_at')
    for conv in all_conversations:
        conv.recipient = conv.participants.exclude(id=request.user.id).first()
    
    return render(request, 'chat/chat_detail.html', {
        'conversation': conversation,
        'chat_messages': messages,
        'recipient': recipient,
        'conversations': all_conversations
    })

@login_required
def send_message(request, conversation_id):
    conversation = get_object_or_404(request.user.conversations, id=conversation_id)
    text = request.POST.get('text')
    if text:
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            text=text
        )
        conversation.save() # Update updated_at
        return render(request, 'chat/partials/message.html', {'msg': message})
    return HttpResponse(status=204)

@login_required
def get_messages(request, conversation_id):
    conversation = get_object_or_404(request.user.conversations, id=conversation_id)
    messages = conversation.messages.all()
    return render(request, 'chat/partials/message_list.html', {'chat_messages': messages})

@login_required
def start_chat(request, user_id):
    recipient = get_object_or_404(User, id=user_id)
    if recipient == request.user:
        return redirect('chat:chat_list')
        
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=recipient).first()
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
    
    return redirect('chat:chat_detail', conversation_id=conversation.id)
