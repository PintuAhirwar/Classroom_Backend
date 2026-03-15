# admin.py
from django.contrib import admin
from .models import Voucher, Order, OrderItem

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("code", "course", "discount_amount", "is_active", "used_count", "usage_limit")
    list_filter = ("is_active", "course")
    search_fields = ("code",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "get_user_email", "final_amount", "payment_status", "created_at")
    list_filter = ("payment_status", "created_at")
    search_fields = ("name", "email", "phone")
    actions = ["mark_success"]

    def get_user_email(self, obj):
        return obj.user.email if obj.user else "Anonymous"
    get_user_email.short_description = "User Email"
    
    @admin.action(description="Mark payment as SUCCESS")
    def mark_success(self, request, queryset):
        queryset.update(payment_status="SUCCESS")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "course", "price")
