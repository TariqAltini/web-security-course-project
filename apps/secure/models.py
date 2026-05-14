from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from decimal import *
from .helpers import generate_api_key
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class ShopUser(AbstractUser):
    # role = 1 is admin, role = 2 is normal user
    role = models.IntegerField(null=True, blank=True)
    avatar = models.ImageField(upload_to="avatar/", default="avatar/avatar-placeholder.png", blank=True)
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="secure_users",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="secure_users",
        blank=True
    )

    class Meta:
        app_label = "secure"

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to="product-image/", blank=True, null=True, default="product-image/coat_img.webp")
    
    class Meta:
        app_label="secure"

class CartItems(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    class Meta:
        app_label="secure"


class Wallet(models.Model):
    key = models.CharField(max_length=64, default=generate_api_key, unique=True)
    user = models.OneToOneField(ShopUser, on_delete=models.CASCADE, related_name="wallet")
    credit = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("100.00"))


@receiver(post_save, sender=ShopUser)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)