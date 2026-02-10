import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer
import uuid
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

class ChatView(APIView):
    permission_classes = [permissions.AllowAny] 

    def post(self, request):
        question = request.data.get('question')
        session_id = request.data.get('sessionId')
        clear_history = request.data.get('clearHistory', False)

        if not question:
            return Response({'error': 'Missing question'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or Create Session
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:16]}"
            session, created = ChatSession.objects.get_or_create(session_id=session_id)
        else:
            session, created = ChatSession.objects.get_or_create(session_id=session_id)

        # Clear history if requested
        if clear_history:
            session.messages.all().delete()

        # Build History for Gemini
        # Fetch last 20 messages to keep context window manageable
        db_history = session.messages.all().order_by('timestamp')[:20] 
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
                'conversationLength': session.messages.count()
            })

        except Exception as e:
            logger.error(f"Gemini Error: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class ChatHistoryView(APIView):
    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id)
            serializer = ChatSessionSerializer(session)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id)
            session.delete()
            return Response({'message': 'Conversation history cleared'})
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
