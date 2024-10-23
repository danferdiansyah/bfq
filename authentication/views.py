import datetime
from .models import CustomUser
from .forms import UserRegistrationForm, UserLoginForm
from .decorators import role_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Set cookie untuk 'last_login'
            response = HttpResponseRedirect(reverse("main:show_main"))
            response.set_cookie('last_login', str(datetime.datetime.now()))

            # Redirect ke dashboard sesuai role
            if user.role == 'customer':
                return redirect('customer_dashboard')
            elif user.role == 'admin':
                return redirect('admin_dashboard')

        else:
            # Tambahkan pesan error jika login gagal
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm(request)

    context = {'form': form}
    return render(request, 'login.html', context)

@login_required
@role_required('customer')
def customer_dashboard(request):
    return render(request, 'main_customer.html')

@login_required
@role_required('admin')
def admin_dashboard(request):
    return render(request, 'main_admin.html')

@login_required
def profile(request):
    user = request.user
    return render(request, 'user_profile.html', {'user': user})


def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response