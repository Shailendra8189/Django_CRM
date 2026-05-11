from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from model_utils import Choices


class Manager(AbstractUser):
    choices = Choices("organizer", "agent", "lead")
    role = models.CharField(max_length=20, choices=choices, default=choices.organizer)


class Lead(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="lead_profile")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_leads")
    created_at = models.DateTimeField(auto_now_add=True)
    agent = models.ForeignKey(
        "agent.Agent", null=True, blank=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        "Category",
        related_name="leads",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    msg = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    type = models.CharField(max_length=20, null=True, blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.type
