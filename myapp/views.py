from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import logout


# Create your views here.
def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()
                messages.success(request, 'Account created successfully!')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['login_success'] = True
            return redirect('home')  # Redirect to Send Email page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully.')  # 👈 show only on login page
    return redirect('login')

@login_required(login_url='login')
def home(request):
    if request.session.pop('login_success', None):  # ✅ Show login success only once
        messages.success(request, 'Login successful!')

    if request.method == 'POST':
        to_email = request.POST.get('to_email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        attachment = request.FILES.get('attachment')

        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=[to_email],
            )
            if attachment:
                email.attach(attachment.name, attachment.read(), attachment.content_type)
            email.send()
            messages.success(request, 'Email sent successfully!')  # 👈 set message here
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')

    return render(request, 'home.html')



