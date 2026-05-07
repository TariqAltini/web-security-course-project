from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from decimal import *

# Create your models here.
class ShopUser(AbstractUser):
    role = models.IntegerField(null=True, blank=True)
    store_credit = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0.0))
    
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
    image = models.ImageField(upload_to="product-image/", blank=True, null=True)
    
    class Meta:
        app_label="secure"

class CartItems(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    class Meta:
        app_label="secure"