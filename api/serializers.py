from rest_framework import serializers
from .models import Slider, Faculty, Testimonial, Marks, demofile, demolecture, FloatingCard, Enquiry
from django.contrib.auth import authenticate
from .models import CustomUser
from courses.models import Lecture, Book


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
        fields = ["id", "name", "email", "phone"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["name", "email", "phone", "password"]  
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_active = False
        user.is_verified = False
        user.save()
        return user

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "name"]
        
class FloatingCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FloatingCard
        fields = ['id', 'label', 'sub_label', 'icon', 'icon_color', 'bg_color', 'position_index']
 
 
class SliderSerializer(serializers.ModelSerializer):
    floating_cards = FloatingCardSerializer(many=True, read_only=True)
 
    class Meta:
        model = Slider
        fields = [
            'id', 'title', 'description',
            'desktop_image', 'mobile_image',
            'show_search', 'is_active',
            'floating_cards',
        ]

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'subject', 'image', 'instagram', 'youtube', 'linkedin', 'is_active']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'feedback', 'image', 'course', 'rating', 'is_active']

class MarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marks
        fields = ['id', 'name', 'image', 'is_active']

class demofileSerializer(serializers.ModelSerializer):
    book_detail = serializers.SerializerMethodField()

    class Meta:
        model = demofile
        fields = ['id', 'name', 'description', 'image', 'urls', 'is_active', 'book', 'book_detail']

    def get_book_detail(self, obj):
        if not obj.book:
            return None
        return {
            'id':    obj.book.id,
            'title': obj.book.title,
            'slug':  obj.book.slug,
            'price': str(obj.book.price),
            'image': str(obj.book.image) if obj.book.image else None,
        }

class demolectureSerializer(serializers.ModelSerializer):
    lecture_detail = serializers.SerializerMethodField()

    class Meta:
        model = demolecture
        fields = ['id', 'title', 'description', 'url', 'is_active', 'lecture', 'lecture_detail']

    def get_lecture_detail(self, obj):
        if not obj.lecture:
            return None
        return {
            'id':         obj.lecture.id,
            'title':      obj.lecture.title,
            'slug':       obj.lecture.slug,
            'base_price': str(obj.lecture.base_price) if obj.lecture.base_price else None,
            'image':      str(obj.lecture.image) if obj.lecture.image else None,
        }

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']