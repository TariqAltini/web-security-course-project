from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction

from .models import Product, CartItems, ShopUser, Wallet

LOGIN_URL = "/secure/login/"

# Create your views here.
def index(request: HttpRequest):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "secure/index.html", context=context)

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("secure:index")
        else:
            return render(request, "secure/login.html", {"error": "Invalid credentials"})
        
    return render(request, "secure/login.html")

@login_required(login_url=LOGIN_URL)
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("secure:index")


def product_details(request: HttpRequest, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "secure/product.html", context={"product": product})


@login_required(login_url=LOGIN_URL)
def cart(request: HttpRequest):
    cart_items = CartItems.objects.filter(user=request.user)
    context = {"cart_items": cart_items}
    return render(request, "secure/cart.html", context=context)


@login_required(login_url=LOGIN_URL)
@require_POST
def add_to_cart(request: HttpRequest, product_id):
    # get parameters
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    # Check the quantity for security
    if quantity <= 0:
        messages.error(request, "Quantity cant be less than 1")
        return redirect("secure:product_details", product_id=product_id)

    # add item to cart and increment if already in cart
    try:
        cart_item = CartItems.objects.get(user=request.user, product=product)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItems.DoesNotExist:
        cart_item = CartItems(user=request.user, product=product, quantity=quantity)
        cart_item.save()
        
    messages.success(request, "Product has been added to cart")
    return redirect("secure:product_details", product_id=product_id)


@login_required(login_url=LOGIN_URL)
def admin_panel(request: HttpRequest):
    
    # Check user role for security
    if request.user.role == 1:
        context = {
            "users": ShopUser.objects.all()
        }
        return render(request, "secure/admin-panel.html", context)
    
    return redirect("secure:index")


@login_required(login_url=LOGIN_URL)
@require_POST
def upgrade_user(request: HttpRequest):
    # check user role for security
    if request.user.role == 1:
        user_to_change = ShopUser.objects.get(username=request.POST.get("username"))
        user_to_change.role = 1
        user_to_change.save()
        return redirect("secure:admin_panel")
    
    return redirect("secure:index")


@login_required(login_url=LOGIN_URL)
@require_POST
def downgrade_user(request: HttpRequest):
    # check user role for security
    if request.user.role == 1:
        user_to_change = ShopUser.objects.get(username=request.POST.get("username"))
        user_to_change.role = 2
        user_to_change.save()
        return redirect("secure:admin_panel")
    
    return redirect("secure:index")


@login_required(login_url=LOGIN_URL)
def account(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    context = {"user": user}
    return render(request, "secure/account.html", context=context)


@login_required(login_url=LOGIN_URL)
@require_POST
def update_email(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    new_email = request.POST.get("email", "")
    if new_email:
        user.email = new_email
        user.save()
        return redirect("secure:account")
    else:
        return render(request, "secure/account.html", {"user": user})
    

@login_required(login_url=LOGIN_URL)
@require_POST
def update_avatar(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    
    image_file = request.FILES.get("avatar")

    if image_file:
        user.avatar = image_file
        user.save()

        return redirect("secure:account")
    
    else:
        return redirect("secure:account")
    

@login_required(login_url=LOGIN_URL)
@require_POST
def change_password(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    
    # Get form data
    current_password = request.POST.get("current_password", "").strip()
    new_password = request.POST.get("new_password", "").strip()
    confirm_password = request.POST.get("confirm_password", "").strip()
    
    # Validate all fields are present
    errors = {}
    
    if not current_password:
        errors["current_password"] = "Current password is required."
    
    if not new_password:
        errors["new_password"] = "New password is required."
    
    if not confirm_password:
        errors["confirm_password"] = "Password confirmation is required."
    
    if errors:
        return redirect("secure:account")
    
    # Verify current password
    if not user.check_password(current_password):
        return redirect("secure:account")
    
    # Check if new password matches confirmation
    if new_password != confirm_password:
        return redirect("secure:account")
    
    # Check if new password is same as current password
    if user.check_password(new_password):
        return redirect("secure:account")
    
    # Set new password and save
    try:
        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=["password"])
    except Exception as e:
        return redirect("secure:account")
    
    return redirect("secure:account")

@login_required(login_url=LOGIN_URL)
def payment_methods(request: HttpRequest):
    wallet = request.user.wallet
    return render(request, "secure/payment-methods.html", {"wallet": wallet})