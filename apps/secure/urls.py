from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "secure"
urlpatterns = [
    #path(...)
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("product/<int:product_id>/", views.product_details, name="product_details"),
    path("product/<int:product_id>/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path('admin-panel/', views.protected_admin_panel, name='protected_admin'),
    path('my-cart/', views.protected_user_cart, name='protected_cart'),
    path('referer-admin/', views.referer_based_admin, name='referer_admin'),
    path('admin-panel-secret-x9y8z7-dont-share/', views.unpredictable_admin_panel, name='secret_admin'),
    path('secure-method/', views.secure_method_action, name='secure_method'),
    path('secure-profile/', views.secure_user_profile, name='secure_profile'),
]