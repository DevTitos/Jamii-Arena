from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.models import User,Group
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from hiero.utils import create_new_account
from hiero.ft import associate_token
from random import randint
from accounts.models import Profile, UserWallet
import string
import random
import os
from dotenv import load_dotenv

load_dotenv()


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def assign_user_wallet(name):
    network_type = os.getenv('NETWORK')
    token_id = os.getenv('Token_ID')
    try:
        recipient_id, recipient_private_key, new_account_public_key = create_new_account(name)
        associate_token(recipient_id, recipient_private_key)

        return {
            'status':'success',
            'new_account_public_key': f'{new_account_public_key}',
            'recipient_private_key': f'{recipient_private_key}',
            'recipient_id':f'{recipient_id}'
        }
    except Exception as e:
        print(e)
        return {
            'status':'failed',
            'error':e
        }

def register_view(request):
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    if request.method == "POST":
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        #gender = request.POST.get('gender')
        password = request.POST.get('password')
        password1 = request.POST['password1']
        if password != password1:
            messages.warning(request, "Password does not match, try Again!")
            return redirect('register')
        if email and first_name and last_name and password is not None:
            try:
                User.objects.get(email=email)
                messages.warning(request, "User with that details exist, please login or sign up with unique credentials")
                return redirect("register")
            except Exception as e:
                try:
                    try:
                        response = assign_user_wallet(name=f'{first_name} {last_name}')
                        print(response)
                        if response['status'] == 'success':
                            new_account_public_key = response['new_account_public_key']
                            recipient_private_key = response['recipient_private_key']
                            recipient_id = response['recipient_id']
                        else:
                            messages.warning(request, "An error occured while trying to assign you a wallet, please try again")
                            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    except Exception as e:
                        messages.warning(request, f'Wallet Creation Faile: |{e}')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    nu = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=email)
                    Profile.objects.create(user=nu)
                    UserWallet.objects.create(user=nu, public_key=new_account_public_key, private_key=recipient_private_key, recipient_id=recipient_id)
                    messages.success(request, "Account has been created successfully, please login to continue")
                    return redirect('login')
                except Exception as e:
                    print(e)
                    messages.warning(request, f"An error occured while trying to create your account, please try again")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "All fields are required")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'accounts/register.html')
   
def login_view(request):
    user = request.user
    if user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                try:
                    profile = Profile.objects.get(user=user)
                    wallet = UserWallet.objects.get(user=user)
                except Profile.DoesNotExist:
                    messages.warning(request, "We are finding problems getting your profile, please try again later!")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                except UserWallet.DoesNotExist:
                    messages.warning(request, "We are finding problems getting your Wallet, please try again later!")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                try:
                    login(request, user)
                    current_user =request.user
                    messages.success(request, f"Welcome back, { current_user.first_name }!")
                    return redirect('profile')
                except:#Verify.DoesNotExist
                    messages.warning(request, "An error occured while trying to verify your account, please try again")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.warning(request,"Invalid Username or password")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "All fields are required")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'accounts/auth.html')

@login_required(login_url="login")
def profile(request):
    user = request.user
    return render(request, 'accounts/profile.html')

@login_required(login_url="login")
def register_artist(request):
    pass

def logout_view(request):
    logout(request)
    return redirect("login")
