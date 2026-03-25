from django.urls import path
from .views import ChatView, ChatHistoryView

urlpatterns = [
    path('', ChatView.as_view(), name='chat_action'),
    path('history/<str:session_id>', ChatHistoryView.as_view(), name='chat_history'),
    # Legacy aliases
    path('chat', ChatView.as_view(), name='chat_action_legacy'),
    path('chat/history/<str:session_id>', ChatHistoryView.as_view(), name='chat_history_legacy'),
]
