"""
Chat API Tests for KrishiSaarthi
Tests the chat endpoint authentication, validation, and session management.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from chat.models import ChatSession, ChatMessage
import json


class ChatAuthenticationTestCase(TestCase):
    """Test that chat endpoints require authentication"""

    def setUp(self):
        self.client = Client()

    def test_chat_requires_auth(self):
        """Test that POST /api/chat requires authentication"""
        response = self.client.post(
            '/api/chat',
            json.dumps({'question': 'What is NDVI?'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_chat_history_requires_auth(self):
        """Test that GET /api/chat/history/<id> requires authentication"""
        response = self.client.get('/api/chat/history/test-session-123')
        self.assertEqual(response.status_code, 401)


class ChatValidationTestCase(TestCase):
    """Test chat input validation"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='chatuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Token {self.token.key}'}

    def test_chat_missing_question(self):
        """Test that missing question returns 400"""
        response = self.client.post(
            '/api/chat',
            json.dumps({}),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_chat_empty_question(self):
        """Test that empty question returns 400"""
        response = self.client.post(
            '/api/chat',
            json.dumps({'question': ''}),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 400)


class ChatSessionModelTestCase(TestCase):
    """Test chat model operations"""

    def test_create_session(self):
        """Test creating a chat session"""
        session = ChatSession.objects.create(session_id='test-session-001')
        self.assertEqual(session.session_id, 'test-session-001')

    def test_create_message(self):
        """Test creating chat messages"""
        session = ChatSession.objects.create(session_id='test-session-002')
        msg = ChatMessage.objects.create(session=session, role='user', text='Hello')
        self.assertEqual(msg.role, 'user')
        self.assertEqual(msg.text, 'Hello')
        self.assertEqual(session.messages.count(), 1)

    def test_delete_session_cascades(self):
        """Test that deleting session deletes messages"""
        session = ChatSession.objects.create(session_id='test-session-003')
        ChatMessage.objects.create(session=session, role='user', text='Test')
        ChatMessage.objects.create(session=session, role='model', text='Response')
        
        session.delete()
        self.assertEqual(ChatMessage.objects.filter(session__session_id='test-session-003').count(), 0)

    def test_chat_history_not_found(self):
        """Test that non-existent session returns 404"""
        user = User.objects.create_user(username='histuser', password='testpass')
        token = Token.objects.create(user=user)
        client = Client()
        response = client.get(
            '/api/chat/history/nonexistent-session',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_chat_history(self):
        """Test deleting chat history"""
        user = User.objects.create_user(username='deluser', password='testpass')
        token = Token.objects.create(user=user)
        session = ChatSession.objects.create(session_id='delete-me', user=user)
        ChatMessage.objects.create(session=session, role='user', text='Test')

        client = Client()
        response = client.delete(
            '/api/chat/history/delete-me',
            HTTP_AUTHORIZATION=f'Token {token.key}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ChatSession.objects.filter(session_id='delete-me').exists())


class ChatIDORPreventionTestCase(TestCase):
    """Test that users cannot access other users' chat sessions"""

    def setUp(self):
        self.client = Client()
        self.user_a = User.objects.create_user(username='user_a', password='testpass')
        self.user_b = User.objects.create_user(username='user_b', password='testpass')
        self.token_a = Token.objects.create(user=self.user_a)
        self.token_b = Token.objects.create(user=self.user_b)
        # Create a session owned by user_a
        self.session_a = ChatSession.objects.create(session_id='session-a', user=self.user_a)
        ChatMessage.objects.create(session=self.session_a, role='user', text='Secret question')
        ChatMessage.objects.create(session=self.session_a, role='model', text='Secret answer')

    def test_user_b_cannot_read_user_a_history(self):
        """IDOR: User B must not see User A's chat session"""
        response = self.client.get(
            '/api/chat/history/session-a',
            HTTP_AUTHORIZATION=f'Token {self.token_b.key}'
        )
        self.assertEqual(response.status_code, 404)

    def test_user_b_cannot_delete_user_a_session(self):
        """IDOR: User B must not be able to delete User A's chat session"""
        response = self.client.delete(
            '/api/chat/history/session-a',
            HTTP_AUTHORIZATION=f'Token {self.token_b.key}'
        )
        self.assertEqual(response.status_code, 404)
        # Session should still exist
        self.assertTrue(ChatSession.objects.filter(session_id='session-a').exists())

    def test_owner_can_read_own_session(self):
        """Positive: Owner can read their own session"""
        response = self.client.get(
            '/api/chat/history/session-a',
            HTTP_AUTHORIZATION=f'Token {self.token_a.key}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['messages']), 2)
