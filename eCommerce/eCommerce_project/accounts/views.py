from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import views as auth_views
from .forms import RegisterForm

# Create your views here.
def register(request):
    """
    Handle user registration.
    Creates a new User + Profile and logs the user in automatically.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('store:home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Custom login view.
    Authenticates the user and redirects to the home page on success.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """
    Log the current user out and redirect to the login page.
    """
    logout(request)
    return redirect('accounts:login')