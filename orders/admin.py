# admin.py
from django.contrib import admin
from .models import Voucher, Order

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("code", "course", "discount_amount", "is_active", "used_count", "usage_limit")
    list_filter = ("is_active", "course")
    search_fields = ("code",)

