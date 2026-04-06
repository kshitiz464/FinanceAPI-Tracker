"""
Page views — session-based auth for the web frontend.
These serve the HTML templates and handle login/register/logout.
The API views (JWT-based) remain separate and unchanged.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User


def home_view(request):
    """
    Root page — shows login/register if not authenticated,
    or redirects to dashboard if logged in.
    """
    if request.user.is_authenticated:
        return dashboard_view(request)
    return render(request, 'api/home.html')


def login_view(request):
    """Handle login form submission."""
    if request.method != 'POST':
        return redirect('/')

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')

    if not username or not password:
        return render(request, 'api/home.html', {
            'error': 'Please enter both username and password.'
        })

    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, 'api/home.html', {
            'error': 'Invalid username or password.'
        })

    if not user.is_active:
        return render(request, 'api/home.html', {
            'error': 'This account has been deactivated.'
        })

    login(request, user)
    return redirect('/')


def register_page_view(request):
    """Handle register form submission from the web page."""
    if request.method != 'POST':
        return redirect('/')

    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    role = request.POST.get('role', 'viewer')

    # Validation
    if not username or not email or not password:
        return render(request, 'api/home.html', {
            'error': 'All fields are required.'
        })
    if len(username) < 3:
        return render(request, 'api/home.html', {
            'error': 'Username must be at least 3 characters.'
        })
    if len(password) < 8:
        return render(request, 'api/home.html', {
            'error': 'Password must be at least 8 characters.'
        })
    if User.objects.filter(username=username).exists():
        return render(request, 'api/home.html', {
            'error': f'Username "{username}" is already taken.'
        })
    if User.objects.filter(email=email).exists():
        return render(request, 'api/home.html', {
            'error': f'Email "{email}" is already registered.'
        })
    if role not in ('viewer', 'analyst', 'admin'):
        role = 'viewer'

    user = User.objects.create_user(
        username=username, email=email, password=password, role=role
    )
    # Auto-login after registration
    login(request, user)
    return redirect('/')


def logout_view(request):
    """Logout and redirect to home."""
    logout(request)
    return redirect('/')


def dashboard_view(request):
    """
    Dashboard page — requires authentication.
    Generates a JWT access token for the frontend JS to call API endpoints.
    """
    if not request.user.is_authenticated:
        return redirect('/')

    # Generate a JWT token for the frontend to use with API calls
    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)

    return render(request, 'api/dashboard.html', {
        'access_token': access_token,
    })
