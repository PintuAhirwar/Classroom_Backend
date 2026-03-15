from urllib import response
from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import Slider, Faculty, Testimonial, Marks, demofile, demolecture, CustomUser
from .serializers import SliderSerializer, FacultySerializer, TestimonialSerializer, MarksSerializer, demofileSerializer, demolectureSerializer, ProfileSerializer, RegisterSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate
from rest_framework import status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend


# Create your views here.

def set_jwt_cookies(response, refresh):
    response.set_cookie(
        key="access_token",
        value=str(refresh.access_token),
        httponly=True,
        secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', True),  # Use settings
        samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'None'),
        max_age=60 * 30,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', True),  # Use settings
        samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE', 'None'),  # Use settings
        max_age=60 * 60 * 24,
        path="/",
    )
    return response

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return self.request.user

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.is_verified = False
            user.save()  
            otp = user.generate_otp()

            # Send OTP via email
            send_mail(
                subject="Your Taxhub Edu. OTP Verification Code",
                message=f"Your OTP code is {otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response({'message': 'OTP sent to email.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name="dispatch")
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        print(f"Debug: Stored OTP for {email}:{user.otp}")
        print(f"Debug: Received OTP:{otp}")

        if user.otp == otp:
            user.is_active = True
            user.is_verified = True
            user.otp = ''
            user.save()
            refresh = RefreshToken.for_user(user)
            response = Response(
                {"message": "Account verified successfully",
                 "access": str(refresh.access_token),
                 "refresh": str(refresh),
                 "user": {
                     "id": user.id,
                     "name": user.name,
                     "email": user.email,
                 }},
                status=status.HTTP_200_OK
            )
            return set_jwt_cookies(response, refresh)
        else:
            print(f"Debug: OTP mismatch for {email}")
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_verified:
            return Response({'error': 'Please verify your account first'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        response = Response({
            "message": "Login successful",
            "access": str(refresh.access_token),  # Add this
            "refresh": str(refresh),  # Add this
            "user": {  # Add this
                "id": user.id,
                "name": user.name,
                "email": user.email,
                # Add other fields
            }
        }, status=status.HTTP_200_OK)
        return set_jwt_cookies(response, refresh)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            response = Response({"message": "Logout successful"})
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SliderViewSet(viewsets.ModelViewSet):
    queryset = Slider.objects.filter(is_active=True).order_by('-id')
    serializer_class = SliderSerializer
    permission_classes = [AllowAny]


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.filter(is_active=True).order_by('-id')
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.filter(is_active=True).order_by('-id')
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.filter(is_active=True).order_by('-id')
    serializer_class = MarksSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class demofileViewSet(viewsets.ModelViewSet):
    queryset = demofile.objects.filter(is_active=True).order_by('-id')
    serializer_class = demofileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['book']

class demolectureViewSet(viewsets.ModelViewSet):
    queryset = demolecture.objects.filter(is_active=True).order_by('-id')
    serializer_class = demolectureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['lecture']
