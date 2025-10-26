from rest_framework import serializers
from .models import CartItem
# adjust Course serializer fields to your Course model fields
from api.models import Course

class CourseSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'price', 'image', 'faculty')  # adjust as needed

class CartItemSerializer(serializers.ModelSerializer):
    course = CourseSmallSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), write_only=True, source='course')

    class Meta:
        model = CartItem
        fields = ('id', 'course', 'course_id', 'added_at')
        read_only_fields = ('id', 'course', 'added_at')
