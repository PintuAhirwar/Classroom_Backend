# views.py
from rest_framework import viewsets, permissions
from .models import Order, OrderItem
from .serializers import OrderSerializer, VoucherSerializer
from .models import Voucher, Order
from api.models import Lecture
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.utils import timezone
import qrcode
from io import BytesIO
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.decorators import action


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Order.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="my-orders"
    )
    def my_orders(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

@api_view(["GET"])
@permission_classes([AllowAny])
def generate_upi_link(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    upi_id = "mr.ahirwar7879-3@okicici"
    payee = "Pintu Ahirwar"
    amount = order.final_amount
    note = f"Order#{order.id}"

    upi_link = (
        f"upi://pay?pa={upi_id}"
        f"&pn={payee}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={note}"
    )

    return Response({"upi_link": upi_link})

@api_view(["GET"])
@permission_classes([AllowAny])
def upi_qr(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    upi_id = "mr.ahirwar7879-3@okicici"
    payee = "Pintu Ahirwar"
    amount = order.final_amount
    note = f"Order#{order.id}"

    upi_link = (
        f"upi://pay?pa={upi_id}"
        f"&pn={payee}"
        f"&am={amount}"
        f"&cu=INR"
        f"&tn={note}"
    )

    qr = qrcode.make(upi_link)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")

@api_view(["POST"])
@permission_classes([AllowAny])
def submit_utr(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    order.utr = request.data.get("utr")
    order.payment_status = "VERIFICATION_PENDING"
    order.save()

    return Response({"message": "Verification pending"})

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
        course = Lecture.objects.get(id=course_id)
        voucher = Voucher.objects.create(
            course=course,
            discount_amount=discount,
            code=code,
        )
        return Response({"success": True, "voucher": VoucherSerializer(voucher).data})
    except Lecture.DoesNotExist:
        return Response({"error": "Course not found"}, status=400)
    

@api_view(["POST"])
@permission_classes([AllowAny]) 
def validate_voucher(request):
    code = request.data.get("code")
    course_id = request.data.get("course_id")

    try:
        voucher = Voucher.objects.get(code__iexact=code, course_id=course_id)
        if not voucher.is_valid():
            return Response({"error": "Voucher expired or invalid"}, status=400)
        return Response({
            "success": True,
            "discount_amount": voucher.discount_amount
        })
    except Voucher.DoesNotExist:
        return Response({"error": "Invalid voucher"}, status=400)