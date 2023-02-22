from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from core.models import UserProfile
from user.api.serializers import EmployeeSerializer

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def register_new_employee(sender, instance, created, raw, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
