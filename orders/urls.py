from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, create_voucher, validate_voucher
# from .views import create_razorpay_order

router = DefaultRouter()
router.register(r'', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),  # FIXED
    path("vouchers/create/", create_voucher, name="create_voucher"),
    path("vouchers/validate/", validate_voucher, name="validate_voucher"),
    # path('razorpay/create-order/', create_razorpay_order, name='razorpay-create-order'),
]
