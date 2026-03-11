from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ai_api_key = models.CharField(max_length=255, blank=True, null=True)
    ai_model = models.CharField(max_length=50, default='gemini-2.5-flash')

    def __str__(self):
        return self.user.username

class Task(models.Model):
    import uuid
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planner_tasks')
    task_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='todo')
    priority = models.CharField(max_length=50, default='medium')
    description = models.TextField(blank=True, null=True)
    due_date = models.CharField(max_length=50, blank=True, null=True)
    due_time = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class EmailDraft(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_drafts')
    tone = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    greeting = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    closing = models.CharField(max_length=100, blank=True, null=True)
    signature = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

class Summary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_summaries')
    original_text = models.TextField()
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.user.username} at {self.created_at}"

class AIChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    request_text = models.TextField()
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.user.username} at {self.created_at}"

class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=255)
    date = models.CharField(max_length=50) # Storing as CharField YYYY-MM-DD for simplicity
    start_time = models.CharField(max_length=50) # HH:MM
    end_time = models.CharField(max_length=50) # HH:MM
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title} on {self.date}"



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
