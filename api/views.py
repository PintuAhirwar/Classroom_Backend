from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import Slider, Course, Faculty, Testimonial, Marks, demofile, demolecture, CustomUser
from .serializers import SliderSerializer, CourseSerializer, FacultySerializer, TestimonialSerializer, MarksSerializer, demofileSerializer, demolectureSerializer, ProfileSerializer, RegisterSerializer, UserSerializer
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


# Create your views here.

class ProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = ProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)  # Deactivate until OTP verified
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


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            user.is_active = True
            user.is_verified = True
            user.otp = ''
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Account verified successfully!',
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({
            'message': 'Login successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logout successful"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class SliderViewSet(viewsets.ModelViewSet):
    queryset = Slider.objects.filter(is_active=True).order_by('-id')
    serializer_class = SliderSerializer
    permission_classes = [AllowAny]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_active=True).order_by('-id')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

class demolectureViewSet(viewsets.ModelViewSet):
    queryset = demolecture.objects.filter(is_active=True).order_by('-id')
    serializer_class = demolectureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
