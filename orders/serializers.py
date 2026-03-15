# serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, Voucher

class OrderItemSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title')
    class Meta:
        model = OrderItem
        fields = ["course", "course_title", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "name",
            "email",
            "phone",
            "address",
            "discount_code",
            "discount_amount",
            "total_amount",
            "final_amount",
            "payment_status",
            "utr",
            "items",
            "created_at",
        ]
        read_only_fields = ["user", "created_at", "payment_status", "utr"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order

class VoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voucher
        fields = '__all__'  