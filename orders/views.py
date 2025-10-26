# views.py
from rest_framework import viewsets, permissions
from .models import Order, OrderItem
from .serializers import OrderSerializer, VoucherSerializer
from .models import Voucher
from api.models import Course
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
# import razorpay


# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_razorpay_order(request):
#     data = request.data
#     amount = int(data.get('amount', 0)) * 100  # Razorpay expects paise
#     currency = "INR"
#     receipt = f"order_rcptid_{request.user.id}"
    
#     razorpay_order = client.order.create(dict(amount=amount, currency=currency, receipt=receipt))
    
#     return Response({
#         "order_id": razorpay_order['id'],
#         "amount": razorpay_order['amount'],
#         "currency": razorpay_order['currency']
#     })



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def create_voucher(request):
    """
    Admin creates a voucher for a specific course
    """
    course_id = request.data.get("course")
    discount = request.data.get("discount_amount")
    code = request.data.get("code")

    try:
        course = Course.objects.get(id=course_id)
        voucher = Voucher.objects.create(
            course=course,
            discount_amount=discount,
            code=code,
        )
        return Response({"success": True, "voucher": VoucherSerializer(voucher).data})
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=400)
    
@api_view(["POST"])
def validate_voucher(request):
    code = request.data.get("code")
    course_id = request.data.get("course_id")

    try:
        voucher = Voucher.objects.get(code=code, course_id=course_id)
        if not voucher.is_valid():
            return Response({"error": "Voucher expired or invalid"}, status=400)
        return Response({
            "success": True,
            "discount_amount": voucher.discount_amount
        })
    except Voucher.DoesNotExist:
        return Response({"error": "Invalid voucher"}, status=400)