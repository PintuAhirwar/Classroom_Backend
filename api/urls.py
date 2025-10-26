from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SliderViewSet, CourseViewSet, FacultyViewSet, 
    TestimonialViewSet, MarksViewSet, demofileViewSet, 
    demolectureViewSet, LoginView, RegisterView, VerifyOTPView, ProfileView,
    LogoutView
)


router = DefaultRouter()
router.register(r'slider', SliderViewSet, basename='slider')
router.register(r'course', CourseViewSet, basename='course')
router.register(r'faculty', FacultyViewSet, basename='faculty') 
router.register(r'testimonial', TestimonialViewSet, basename='testimonial')
router.register(r'marks', MarksViewSet, basename='marks')
router.register(r'demofile', demofileViewSet, basename='demofile')
router.register(r'demolecture', demolectureViewSet, basename='demolecture')

urlpatterns = [
    path('', include(router.urls)),

    # Auth endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # JWT refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    ]