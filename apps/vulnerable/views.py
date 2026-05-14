from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
import io

from .models import Product, CartItems, ShopUser, Wallet
from .helpers import authenticate

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

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user, backend="apps.vulnerable.backends.VulnerableBackend")
            response = redirect("vulnerable:index")
            response.set_cookie("role", user.role)
            return response
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
    
    # VULNERABLE: Checks cookies instead of database
    # Cookies can easily be changed
    try:
        role = int(request.COOKIES.get("role", 2))
    except ValueError as e:
        role = 2

    if role == 1:
        context = {
            "users": ShopUser.objects.all()
        }
        return render(request, "vulnerable/admin-panel.html", context)
    
    return redirect("vulnerable:index")


@login_required(login_url=LOGIN_URL)
@require_POST
def upgrade_user(request: HttpRequest):
    # check user role for security
    if request.user.role == 1:
        user_to_change = ShopUser.objects.get(username=request.POST.get("username"))
        user_to_change.role = 1
        user_to_change.save()
        return redirect("vulnerable:admin_panel")
    
    return redirect("vulnerable:index")


@login_required(login_url=LOGIN_URL)
@require_POST
def downgrade_user(request: HttpRequest):
    # check user role for security
    if request.user.role == 1:
        user_to_change = ShopUser.objects.get(username=request.POST.get("username"))
        user_to_change.role = 2
        user_to_change.save()
        return redirect("vulnerable:admin_panel")
    
    return redirect("vulnerable:index")


@login_required(login_url=LOGIN_URL)
def account(request: HttpRequest):
    id = request.GET.get("id")
    try:
        user = ShopUser.objects.get(username=id)
    except ShopUser.DoesNotExist as e:
        return redirect("vulnerable:index")
    
    #VULNERABLE: Response will always contain the account data of the
    # user with the supplied id
    response = render(request, "vulnerable/account.html", {"user": user})

    if id == request.user.username:
        return response
    else:
        # VULNERABLE: response.content should be erased here
        response.status_code = 302
        response.headers["Location"] = reverse("vulnerable:index")
        return response


@login_required(login_url=LOGIN_URL)
@require_POST
def update_email(request: HttpRequest):
    user = get_object_or_404(ShopUser, pk=request.user.pk)
    #VULNERABLE: Mass assignment vulnerability
    #assigns any parameter sent by the user without checking
    for key, value in request.POST.items():
        if hasattr(user, key) and value:
            setattr(user, key, value)

    user.save()
    return redirect("vulnerable:account")
    

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
            user.raw_password = new_password
            user.save(update_fields=["password", "raw_password"])
    except Exception as e:
        return redirect("vulnerable:account")
    
    return redirect("vulnerable:account")


@login_required(login_url=LOGIN_URL)
def payment_methods(request: HttpRequest):
    wallet = request.user.wallet
    return render(request, "secure/payment-methods.html", {"wallet": wallet})


@login_required(login_url=LOGIN_URL)
def payment_methods_download(request: HttpRequest):
    wallet = get_object_or_404(Wallet, user=request.user)
    content = f"For user: {wallet.user}\nWallet key: {wallet.key}"
    buffer = io.BytesIO(content.encode("utf-8"))
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"{wallet.id}.txt")