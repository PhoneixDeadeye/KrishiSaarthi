from django.urls import path
from .views import ChatView, ChatHistoryView

urlpatterns = [
    path('chat', ChatView.as_view(), name='chat_action'),
    path('chat/history/<str:session_id>', ChatHistoryView.as_view(), name='chat_history'),
]
