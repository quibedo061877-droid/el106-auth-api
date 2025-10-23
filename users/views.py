from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .serializers import RegisterSerializer
from .tokens import email_verification_token, password_reset_token
from rest_framework.views import APIView
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.hashers import make_password

def home_page(request):
    return render(request, 'users/home.html')

def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

        token = email_verification_token.make_token(user)
        verify_url = request.build_absolute_uri(f"/verify-email/?uid={user.pk}&token={token}")
        send_mail(
            "Verify your account",
            f"Click to verify: {verify_url}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        messages.success(request, "Registration successful! Check your email (console) for verification link.")
        return redirect('login')

    return render(request, 'users/register.html')

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return redirect('profile')
            else:
                messages.error(request, "Please verify your email first.")
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'users/login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def verify_email(request):
    uid = request.GET.get('uid')
    token = request.GET.get('token')
    user = get_object_or_404(User, pk=uid)
    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'users/verify.html', {"status": "success"})
    return render(request, 'users/verify.html', {"status": "failed"})

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/profile.html', {"user": request.user})

def forgot_password_page(request):
    if request.method == "POST":
        email = request.POST.get('email').strip()
        try:
            user = User.objects.get(email=email)
            token = password_reset_token.make_token(user)
            reset_url = request.build_absolute_uri(f"/reset-password/?uid={user.pk}&token={token}")
            send_mail(
                "Reset Your Password",
                f"Click the link to reset your password: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            messages.success(request, "Password reset link has been sent to your email (console).")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, 'users/forgot_password.html')

def reset_password_page(request):
    uid = request.GET.get("uid")
    token = request.GET.get("token")
    if request.method == "POST":
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path + f"?uid={uid}&token={token}")
        user = get_object_or_404(User, pk=uid)
        if password_reset_token.check_token(user, token):
            user.password = make_password(password)
            user.save()
            messages.success(request, "Password reset successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid or expired reset link.")
            return redirect('forgot-password')
    return render(request, 'users/reset_password.html')

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the currently authenticated user's profile information.",
        responses={
            200: openapi.Response(
                description="User profile details",
                examples={
                    "application/json": {
                        "username": "student01",
                        "email": "student01@example.com",
                        "is_verified": True
                    }
                }
            ),
            401: "Unauthorized – Missing or invalid token",
        },
    )
    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_active,
        }
        return Response(data)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=PasswordResetRequestSerializer,
        operation_description="Request a password reset email.",
        responses={
            200: openapi.Response("Reset link sent"),
            404: "User not found"
        }
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            token = password_reset_token.make_token(user)
            reset_url = request.build_absolute_uri(f"/reset-password/?uid={user.pk}&token={token}")
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_url}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return Response({"message": "Reset link sent to email."})
        except User.DoesNotExist:
            return Response({"error": "No user with this email."}, status=404)
