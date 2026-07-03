from django.db import models
from django.conf import settings

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title      = models.CharField(max_length=200)
    priority   = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date   = models.DateField()
    tags       = models.JSONField(default=list, blank=True)
    order      = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.title