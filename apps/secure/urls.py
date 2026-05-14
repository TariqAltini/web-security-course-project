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
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("account/", views.account, name="account"),
    path("update-email/", views.update_email, name="update_email"),
    path("update-avatar/", views.update_avatar, name="update_avatar"),
    path("change-password/", views.change_password, name="change_password"),
    path("upgrade-user/", views.upgrade_user, name="upgrade_user"),
    path("downgrade-user/", views.downgrade_user, name="downgrade_user"),
    path("payment-methods/", views.payment_methods, name="payment_methods"),
]