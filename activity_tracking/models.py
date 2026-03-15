# activity_tracking/models.py
from django.db import models


class ProductActivity(models.Model):
    ACTION_CHOICES = [
        ("add_to_cart", "Add to Cart"),
        ("buy_now",     "Buy Now"),
    ]

    # Action type
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)

    # Product info
    product_id   = models.CharField(max_length=100, blank=True)
    product_type = models.CharField(max_length=50,  blank=True)   # lecture / book / test_series / combo
    product_name = models.CharField(max_length=500, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Variant info (for lectures)
    variant_mode     = models.CharField(max_length=100, blank=True)
    variant_language = models.CharField(max_length=100, blank=True)

    # User info (optional — filled if user typed name/phone at checkout)
    user_name  = models.CharField(max_length=200, blank=True)
    user_phone = models.CharField(max_length=20,  blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name        = "Product Activity"
        verbose_name_plural = "Product Activities"

    def __str__(self):
        name  = self.user_name  or "Anonymous"
        phone = self.user_phone or "—"
        return f"[{self.get_action_display()}] {self.product_name} | {name} ({phone}) | {self.created_at:%d %b %Y %H:%M}"