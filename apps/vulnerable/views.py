from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Product, CartItems, ShopUser

# Create your views here.
def index(request: HttpRequest):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "vulnerable/index.html", context=context)

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("vulnerable:index")
        else:
            return render(request, "vulnerable/login.html", {"error": "Invalid credentials"})
        
    return render(request, "vulnerable/login.html")

@login_required(login_url="vulnerable/login")
def logout_view(request: HttpRequest):
    logout(request)
    return redirect("index")


def product_details(request: HttpRequest, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "vulnerable/product.html", context={"product": product})


@login_required(login_url="/vulnerable/login")
def cart(request: HttpRequest):
    cart_items = CartItems.objects.filter(user=request.user)
    context = {"cart_items": cart_items}
    return render(request, "vulnerable/cart.html", context=context)


@login_required(login_url="/vulnerable/login")
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
    return redirect("product_details", product_id=product_id)


@login_required(login_url="/secure/login")
def admin_panel(request: HttpRequest):
    
    # Check user role for security
    if request.user.role == 1:
        context = {
            "users": ShopUser.objects.all()
        }
        return render(request, "secure/admin-panel.html", context)
    
    return redirect("index")