# activity_tracking/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductActivity


@admin.register(ProductActivity)
class ProductActivityAdmin(admin.ModelAdmin):

    # ── List view ─────────────────────────────────────────────────────────────
    list_display = [
        "created_at_fmt",
        "action_badge",
        "product_name",
        "product_type",
        "price_fmt",
        "variant_info",
        "user_name",
        "user_phone",
    ]

    list_filter  = ["action", "product_type", "created_at"]
    search_fields = ["product_name", "user_name", "user_phone", "product_id"]
    readonly_fields = [
        "action", "product_id", "product_type", "product_name", "product_price",
        "variant_mode", "variant_language", "user_name", "user_phone", "created_at",
    ]
    ordering = ["-created_at"]
    list_per_page = 50
    date_hierarchy = "created_at"

    # ── Custom columns ────────────────────────────────────────────────────────
    @admin.display(description="Time", ordering="created_at")
    def created_at_fmt(self, obj):
        return obj.created_at.strftime("%d %b %Y  %H:%M")

    @admin.display(description="Action")
    def action_badge(self, obj):
        if obj.action == "add_to_cart":
            color = "#2563eb"   # blue
            label = "🛒 Add to Cart"
        else:
            color = "#16a34a"   # green
            label = "⚡ Buy Now"
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600">{}</span>',
            color, label
        )

    @admin.display(description="Price")
    def price_fmt(self, obj):
        if obj.product_price:
            return f"₹{obj.product_price:,.0f}"
        return "—"

    @admin.display(description="Variant")
    def variant_info(self, obj):
        parts = [p for p in [obj.variant_mode, obj.variant_language] if p]
        return " · ".join(parts) if parts else "—"

    # ── Disable add/delete from admin (read-only log) ─────────────────────────
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser   # only superuser can delete