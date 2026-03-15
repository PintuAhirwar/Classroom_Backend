from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
    create_voucher,
    validate_voucher,
    generate_upi_link,  # Ensure this is imported from views.py
    upi_qr,             # Ensure this is imported from views.py
    submit_utr          # Ensure this is imported from views.py
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),  # FIXED
    path("vouchers/create/", create_voucher, name="create_voucher"),
    path("vouchers/validate/", validate_voucher, name="validate_voucher"),
    
    path('<int:order_id>/upi/', generate_upi_link, name='generate_upi_link'),
    path('<int:order_id>/upi-qr/', upi_qr, name='upi_qr'),
    path('<int:order_id>/submit-utr/', submit_utr, name='submit_utr'),

]
