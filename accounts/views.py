from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if request.htmx:
                return render(request, "accounts/partials/login_success.html", {"user": user})
            return redirect("home")
        else:
            if request.htmx:
                return render(request, "accounts/partials/login_form.html", {"error": "Invalid credentials"})
            messages.error(request, "Invalid credentials")
    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/partials/register_form.html", {"error": "Username taken"})

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        if request.htmx:
            return render(request, "accounts/partials/register_success.html", {"user": user})
        return redirect("home")

    return render(request, "accounts/register.html")


def logout_view(request):
    logout(request)
    return redirect("accounts:login")
