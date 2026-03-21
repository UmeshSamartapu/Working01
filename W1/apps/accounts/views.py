from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm


# 🔐 Signup
def signup_view(request):
    form = SignupForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('login')

    return render(request, 'accounts/signup.html', {'form': form})


# 🔐 Login
def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🎯 ROLE-BASED REDIRECT (SAFE VERSION)
            if user.role == 'admin':
                return redirect('admin:index')  # Django admin
            elif user.role == 'doctor':
                return redirect('doctor_dashboard')
            elif user.role == 'technician':
                return redirect('technician_dashboard')
            else:
                return redirect('dashboard')  # fallback

        else:
            error = "Invalid username or password"

    return render(request, 'accounts/login.html', {'error': error})


# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('login')