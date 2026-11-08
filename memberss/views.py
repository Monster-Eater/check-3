from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django import forms
from django.contrib import messages 
from . forms import SignUpForm, ProfilePicForm, UpdateUserForm, ChangePasswordFrom
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from home.models import Profile



def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            messages.success(request, ('You Have Been Logged In...!'))
            return redirect('home')
        else:
            messages.success(request, ('There Was an error logging in. Please Try Again...!'))
            return redirect('login')
    else:
       return render (request, 'registration/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ('Hey! You have Been logged out...'))
    return redirect ('home')
   
def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email = form.cleaned_data['email']
            user = authenticate(username = username , password = password)
            login(request, user)
            messages.success(request, ('You have successfully registered. Wellcom...!'))
            return redirect('home')
        
    return render(request, 'registration/register.html', {'form': form})

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id = request.user.id)
        profile_user = Profile.objects.get(user__id = request.user.id)
        user_form = UpdateUserForm(request.POST or None, request.FILES or None,instance= current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance= profile_user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            login(request, current_user)
            messages.success(request, ('Your profile Has Been Updated...!'))
            return redirect('home')  
        else:
            return render(request, 'registration/update_user.html', {'user_form': user_form, 'profile_form': profile_form})  
    else:
        messages.success(request, ('You Must Be Logged In To View That Page...!')) 
        return redirect('home')  
    
def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = ChangePasswordFrom(current_user, request.POST)
            if form.is_valid():
               form.save()
               messages.success(request, ('Your password has been updated...! Please Login..'))
               return redirect('login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)  
                    return redirect('update_password') 
        else:
            form = ChangePasswordFrom(current_user)
            return render(request, 'registration/update_password.html', {'form': form})
    else:
        messages.successs(request, ('You must be loggesd in to view that page...!'))
        return redirect('home')       
       






