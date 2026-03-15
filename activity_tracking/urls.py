# activity_tracking/urls.py
from django.urls import path
from .views import TrackActivityView

urlpatterns = [
    path("track/", TrackActivityView.as_view(), name="track-activity"),
]