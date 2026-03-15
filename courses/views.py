from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from .models import (
    Category, Subject,
    Lecture,
    Book,
    TestSeries,
    ComboProduct,
)
from .serializers import (
    CategorySerializer, SubjectSerializer,
    LectureSerializer, LectureListSerializer,
    BookSerializer,
    TestSeriesSerializer,
    ComboProductSerializer, ComboProductListSerializer,
)


# ─────────────────────────────────────────────────────────────
# PAGINATION
# ─────────────────────────────────────────────────────────────

class StandardPagination(PageNumberPagination):
    page_size              = 12
    page_size_query_param  = 'page_size'   # ?page_size=24
    max_page_size          = 100


# ─────────────────────────────────────────────────────────────
# CATEGORY / SUBJECT  (no pagination — used as filter data)
# ─────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    queryset           = Category.objects.filter(is_active=True).prefetch_related('subjects').order_by('name')
    serializer_class   = CategorySerializer
    permission_classes = [permissions.AllowAny]


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class   = SubjectSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Subject.objects.filter(is_active=True).order_by('name')
        if cat := self.request.query_params.get('category'):
            qs = qs.filter(category__slug=cat)
        return qs


# ─────────────────────────────────────────────────────────────
# LECTURE
# ─────────────────────────────────────────────────────────────

class LectureViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class   = StandardPagination

    def get_serializer_class(self):
        return LectureListSerializer if self.action == 'list' else LectureSerializer

    def get_queryset(self):
        qs = (Lecture.objects
              .filter(is_active=True)
              .select_related('faculty', 'category', 'subject')
              .prefetch_related('variants', 'curriculum',
                                'recommended_books', 'recommended_test_series')
              .order_by('-created_at'))
        p = self.request.query_params
        if p.get('category'):   qs = qs.filter(category__slug=p['category'])
        if p.get('subject'):    qs = qs.filter(subject__slug=p['subject'])
        if p.get('faculty'):    qs = qs.filter(faculty__id=p['faculty'])
        if p.get('batch_type'): qs = qs.filter(batch_type=p['batch_type'])
        if p.get('featured'):   qs = qs.filter(is_featured=True)
        if p.get('search'):
            qs = qs.filter(
                Q(title__icontains=p['search']) |
                Q(faculty__name__icontains=p['search'])
            )
        return qs

    def get_object(self):
        qs     = self.get_queryset()
        lookup = self.kwargs.get(self.lookup_field)
        try:
            return qs.get(id=int(lookup))
        except (ValueError, TypeError, Lecture.DoesNotExist):
            return qs.get(slug=lookup)


# ─────────────────────────────────────────────────────────────
# BOOK
# ─────────────────────────────────────────────────────────────

class BookViewSet(viewsets.ModelViewSet):
    serializer_class   = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class   = StandardPagination

    def get_queryset(self):
        qs = (Book.objects
              .filter(is_active=True)
              .select_related('faculty', 'category', 'subject')
              .order_by('-created_at'))          # 'sets' prefetch REMOVED
        p = self.request.query_params
        if p.get('category'):  qs = qs.filter(category__slug=p['category'])
        if p.get('subject'):   qs = qs.filter(subject__slug=p['subject'])
        if p.get('faculty'):   qs = qs.filter(faculty__id=p['faculty'])
        if p.get('book_type'): qs = qs.filter(book_type=p['book_type'])
        if p.get('featured'):  qs = qs.filter(is_featured=True)
        if p.get('search'):
            qs = qs.filter(
                Q(title__icontains=p['search']) |
                Q(faculty__name__icontains=p['search'])
            )
        return qs

    def get_object(self):
        qs     = self.get_queryset()
        lookup = self.kwargs.get(self.lookup_field)
        try:    return qs.get(id=int(lookup))
        except: return qs.get(slug=lookup)


# ─────────────────────────────────────────────────────────────
# TEST SERIES
# ─────────────────────────────────────────────────────────────

class TestSeriesViewSet(viewsets.ModelViewSet):
    serializer_class   = TestSeriesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class   = StandardPagination

    def get_queryset(self):
        qs = (TestSeries.objects
              .filter(is_active=True)
              .select_related('faculty', 'category', 'subject')
              .order_by('-created_at'))
        p = self.request.query_params
        if p.get('course_name'): qs = qs.filter(course_name=p['course_name'])
        if p.get('level'):       qs = qs.filter(level=p['level'])
        if p.get('category'):    qs = qs.filter(category__slug=p['category'])
        if p.get('subject'):     qs = qs.filter(subject__slug=p['subject'])
        if p.get('faculty'):     qs = qs.filter(faculty__id=p['faculty'])
        if p.get('test_type'):   qs = qs.filter(test_type=p['test_type'])
        if p.get('featured'):    qs = qs.filter(is_featured=True)
        if p.get('search'):      qs = qs.filter(title__icontains=p['search'])
        return qs

    def get_object(self):
        qs     = self.get_queryset()
        lookup = self.kwargs.get(self.lookup_field)
        try:    return qs.get(id=int(lookup))
        except: return qs.get(slug=lookup)


# ─────────────────────────────────────────────────────────────
# COMBO
# ─────────────────────────────────────────────────────────────

class ComboProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class   = StandardPagination

    def get_serializer_class(self):
        return ComboProductListSerializer if self.action == 'list' else ComboProductSerializer

    def get_queryset(self):
        qs = (ComboProduct.objects
              .filter(is_active=True)
              .prefetch_related(
                  'lectures', 'lectures__variants',
                  'lectures__faculty', 'lectures__category', 'lectures__subject',
                  'books', 'books__faculty', 'books__category', 'books__subject',
                  'test_series', 'test_series__faculty',
                  'test_series__category', 'test_series__subject',
              )
              .order_by('-created_at'))
        if self.request.query_params.get('featured'):
            qs = qs.filter(is_featured=True)
        return qs

    def get_object(self):
        qs     = self.get_queryset()
        lookup = self.kwargs.get(self.lookup_field)
        try:    return qs.get(id=int(lookup))
        except: return qs.get(slug=lookup)