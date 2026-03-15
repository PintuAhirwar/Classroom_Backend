from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SubjectViewSet,
    LectureViewSet,
    BookViewSet,
    TestSeriesViewSet,
    ComboProductViewSet,
)

router = DefaultRouter()
router.register(r'category',    CategoryViewSet,    basename='category')
router.register(r'subject',     SubjectViewSet,     basename='subject')
router.register(r'lectures',    LectureViewSet,     basename='lectures')
router.register(r'books',       BookViewSet,        basename='books')
router.register(r'test-series', TestSeriesViewSet,  basename='test-series')
router.register(r'combos',      ComboProductViewSet, basename='combos')

urlpatterns = [
    path('', include(router.urls)),
]