# vulnerable/backends.py
from django.contrib.auth.backends import ModelBackend
from apps.vulnerable.models import ShopUser

class VulnerableBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = ShopUser.objects.using("vulnerable_db").get(username=username)
            if user.check_password(password):
                return user
        except ShopUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ShopUser.objects.using("vulnerable_db").get(pk=user_id)
        except ShopUser.DoesNotExist:
            return None