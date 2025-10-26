from rest_framework import serializers
from .models import Slider, Course, Faculty, Testimonial, Marks, demofile, demolecture
from django.contrib.auth import authenticate
from .models import CustomUser


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "name", "email", "phone", "address", "bio", "profile_pic", "dob"]
        extra_kwargs = {
            'email': {'required': True},
            'phone': {'required': True},
        }
    def validate_email(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone(self, value):
        user = self.context['request'].user
        if CustomUser.objects.exclude(pk=user.pk).filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "name", "mobile"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["name", "email", "phone", "password"]  
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False  # deactivate until OTP verified
        user.save()
        return user


class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = ['id', 'title', 'description', 'image', 'is_active']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'faculty', 'image', 'price', 'is_active']

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'subject', 'social_media', 'image', 'is_active']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'feedback', 'image', 'course', 'rating', 'is_active']

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = ['id', 'name', 'image', 'is_active']

class demofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = demofile
        fields = ['id', 'name', 'image', 'urls', 'description', 'is_active']

class demolectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = demolecture
        fields = ['id', 'title', 'url', 'description', 'is_active']

