# activity_tracking/serializers.py
from rest_framework import serializers
from .models import ProductActivity


class ProductActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductActivity
        fields = [
            "id",
            "action",
            "product_id",
            "product_type",
            "product_name",
            "product_price",
            "variant_mode",
            "variant_language",
            "user_name",
            "user_phone",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]