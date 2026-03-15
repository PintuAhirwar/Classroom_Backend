# activity_tracking/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ProductActivity
from .serializers import ProductActivitySerializer


class TrackActivityView(APIView):
    """
    POST /api/activity/track/
    No authentication required — anyone can log an activity.
    """
    authentication_classes = []
    permission_classes     = []

    def post(self, request):
        serializer = ProductActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)