from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "vulnerable"
urlpatterns = [
    #path(...)
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("product/<int:product_id>/", views.product_details, name="product_details"),
    path("product/<int:product_id>/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
]