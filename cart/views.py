from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CartItem
from .serializers import CartItemSerializer
from api.models import Course

class CartListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user).select_related('course')
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        # expects { "course_id": <id> }
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            course = serializer.validated_data['course']
            obj, created = CartItem.objects.get_or_create(user=request.user, course=course)
            out = CartItemSerializer(obj)
            return Response(out.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartRemoveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, course_id):
        try:
            item = CartItem.objects.get(user=request.user, course_id=course_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

class CartClearAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response({"detail": "Cleared"}, status=status.HTTP_200_OK)
