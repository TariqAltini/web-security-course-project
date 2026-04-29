from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class ShopUser(AbstractUser):
    role_id = models.IntegerField()
    store_credit = models.DecimalField(max_digits=6, decimal_places=2)

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField()

class CartItems(models.Model):
    cart_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()