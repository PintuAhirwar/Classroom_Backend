from django.db import models
from django.conf import settings
from courses.models import Lecture  # adjust app name

User = settings.AUTH_USER_MODEL

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    course = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='in_carts')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user} - {self.course}" 
