from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session {self.session_id} - {self.user}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('model', 'Model'),
    ]

    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField(max_length=10000, help_text='Message content, max 10k chars')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.role}: {self.text[:50]}..."
