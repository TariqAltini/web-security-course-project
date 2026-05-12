from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction

from .models import Product, CartItems, ShopUser

LOGIN_URL = "/vulnerable/login/"

# Create your views here.
def index(request: HttpRequest):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "vulnerable/index.html", context=context)

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("vulnerable:index")
        else:
            return render(request, "vulnerable/login.html", {"error": "Invalid credentials"})
        
    return render(request, "vulnerable/login.html")

@login_required(login_url=LOGIN_URL)
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("vulnerable:index")


def product_details(request: HttpRequest, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "vulnerable/product.html", context={"product": product})


@login_required(login_url=LOGIN_URL)
def cart(request: HttpRequest):
    cart_items = CartItems.objects.filter(user=request.user)
    context = {"cart_items": cart_items}
    return render(request, "vulnerable/cart.html", context=context)


@login_required(login_url=LOGIN_URL)
@require_POST
def add_to_cart(request: HttpRequest, product_id):
    # get parameters
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))

    # VULNERABILITY HERE: HIGH-LEVEL LOGIC VULNERABILITY
    # This is vulnerable due to not checking for quantity boundaries

    # add item to cart and increment if already in cart
    try:
        cart_item = CartItems.objects.get(user=request.user, product=product)
        cart_item.quantity += quantity
        cart_item.save()
    except CartItems.DoesNotExist:
        cart_item = CartItems(user=request.user, product=product, quantity=quantity)
        cart_item.save()
        
    messages.success(request, "Product has been added to cart")
    return redirect("vulnerable:product_details", product_id=product_id)


@login_required(login_url=LOGIN_URL)
def admin_panel(request: HttpRequest):
    
    # Check user role for security
    if request.user.role == 1:
        context = {
            "users": ShopUser.objects.all()
        }
        return render(request, "vulnerable/admin-panel.html", context)
    
    return redirect("vulnerable:index")


@login_required(login_url=LOGIN_URL)
def account(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    context = {"user": user}
    return render(request, "vulnerable/account.html", context=context)


@login_required(login_url=LOGIN_URL)
@require_POST
def update_email(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    new_email = request.POST.get("email", "")
    if new_email:
        user.email = new_email
        user.save()
        return redirect("vulnerable:account")
    else:
        return render(request, "vulnerable/account.html", {"user": user})
    

@login_required(login_url=LOGIN_URL)
@require_POST
def update_avatar(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    
    image_file = request.FILES.get("avatar")

    if image_file:
        user.avatar = image_file
        user.save()

        return redirect("vulnerable:account")
    
    else:
        return redirect("vulnerable:account")
    

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
        return redirect("vulnerable:account")
    
    # Verify current password
    if not user.check_password(current_password):
        return redirect("vulnerable:account")
    
    # Check if new password matches confirmation
    if new_password != confirm_password:
        return redirect("vulnerable:account")
    
    # Check if new password is same as current password
    if user.check_password(new_password):
        return redirect("vulnerable:account")
    
    # Set new password and save
    try:
        with transaction.atomic():
            user.set_password(new_password)
            user.save(update_fields=["password"])
    except Exception as e:
        return redirect("vulnerable:account")
    
    return redirect("vulnerable:account")
