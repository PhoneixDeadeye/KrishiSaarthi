import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer
from config.throttling import GeminiChatThrottle
import uuid
import logging

logger = logging.getLogger(__name__)

# Configure Gemini once at module level
_gemini_api_key = os.environ.get('GEMINI_API_KEY')
if _gemini_api_key:
    genai.configure(api_key=_gemini_api_key)

# Maximum messages to keep in context window
MAX_CONTEXT_MESSAGES = 20
# Maximum question length (characters)
MAX_QUESTION_LENGTH = 4000


class ChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [GeminiChatThrottle]

    def post(self, request):
        if not _gemini_api_key:
            # Lazy re-check at request time in case env was set after import
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                return Response({'error': 'Chat service not configured'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        question = request.data.get('question', '').strip()
        session_id = request.data.get('sessionId')
        clear_history = request.data.get('clearHistory', False)

        if not question:
            return Response({'error': 'Missing question'}, status=status.HTTP_400_BAD_REQUEST)

        if len(question) > MAX_QUESTION_LENGTH:
            return Response(
                {'error': f'Question too long. Maximum {MAX_QUESTION_LENGTH} characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or Create Session — always scoped to the requesting user
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:16]}"

        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user}
        )

        # Ensure session belongs to this user (prevents IDOR)
        if session.user and session.user != request.user:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        # Backfill user on legacy sessions that have user=None
        if session.user is None:
            session.user = request.user
            session.save(update_fields=['user'])

        # Clear history if requested
        if clear_history:
            session.messages.all().delete()

        # Build History for Gemini
        # Use a subquery-based approach to avoid Python-side reversal  
        db_history = list(
            ChatMessage.objects.filter(session=session)
            .order_by('-timestamp')[:MAX_CONTEXT_MESSAGES]
        )
        db_history.reverse()  # Reverse the small list in memory (max 20 items)

        chat_history = []
        for msg in db_history:
            chat_history.append({
                "role": "model" if msg.role == "model" else "user",
                "parts": [msg.text],
            })

        # System Instruction
        system_instruction = """You are an agricultural assistant chatbot helping farmers and professionals.
Core expertise: crop management, fertilizers, plant disease and pest control, soil health, irrigation, seasonal guidance, weather impact, market prices, carbon credits, and sustainable practices.
Guidelines:
Always reply in the language of the user.
Give clear, practical, and concise advice (2 to 4 sentences).
Avoid jargon; keep explanations simple.
Emphasize safety and sustainable methods.
For market prices, note variation by region and time.
Ask for location details if conditions differ by region.
Redirect politely if asked about non-agriculture topics.
Goal: Improve farm productivity, sustainability, and farmer success with actionable guidance."""

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_instruction
            )

            chat = model.start_chat(history=chat_history)
            response = chat.send_message(question)

            reply_text = response.text

            # Save Messages to DB
            ChatMessage.objects.create(session=session, role='user', text=question)
            ChatMessage.objects.create(session=session, role='model', text=reply_text)

            return Response({
                'reply': reply_text,
                'sessionId': session.session_id,
                'conversationLength': len(db_history) + 2  # Avoid extra COUNT query
            })

        except Exception as e:
            logger.error("Gemini Error: %s", e, exc_info=True)
            return Response({'error': 'Chat service temporarily unavailable'}, status=status.HTTP_502_BAD_GATEWAY)

class ChatHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
            session.delete()
            return Response({'message': 'Conversation history cleared'})
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
