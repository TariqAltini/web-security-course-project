from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from .models import Product, CartItems

# Create your views here.
def index(request: HttpRequest):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "secure/index.html", context=context)

def login_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "secure/login.html", {"error": "Invalid credentials"})
        
    return render(request, "secure/login.html")

def logout_view(request: HttpRequest):
    logout(request)
    redirect("index")