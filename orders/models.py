from django.db import models
from django.conf import settings
from courses.models import Lecture
from django.utils import timezone

# Define STATUS choices (must be defined before use)
STATUS = [
    ("PENDING", "Pending"),
    ("VERIFICATION_PENDING", "Verification Pending"),
    ("SUCCESS", "Success"),
    ("REJECTED", "Rejected"),
]
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    discount_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="PENDING"
    )
    utr = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_email = self.user.email if self.user else "Anonymous"
        return f"Order #{self.id} - {user_email}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    course = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.course.title

class Voucher(models.Model):
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="vouchers")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=1)  # how many times it can be used
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False

        if self.valid_from and self.valid_from > now:
            return False

        if self.valid_to and now > self.valid_to:
            return False

        if self.used_count >= self.usage_limit:
            return False

        return True

    def __str__(self):
        return f"{self.code} - {self.course.title}"
