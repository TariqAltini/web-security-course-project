from .models import ShopUser

def authenticate(username: str, password: str):
    try:
        user = ShopUser.objects.get(username=username)
    except ShopUser.DoesNotExist as e:
        return None

    if user.check_password(password):
        return user
    else:
        return None