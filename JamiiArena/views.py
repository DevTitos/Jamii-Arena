from django.shortcuts import render, redirect
from hiero.utils import create_new_account

def home(request):
    return render(request, 'index.html')


def dashboard(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'dashboard.html')
    return redirect('login')