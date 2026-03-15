from rest_framework import serializers
from .models import (
    Category, Subject,
    Lecture, LectureVariant, LectureCurriculumItem,
    Book,
    TestSeries,
    ComboProduct,
)


# ─────────────────────────────────────────────────────────────
# SHARED
# ─────────────────────────────────────────────────────────────

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Subject
        fields = ['id', 'name', 'slug', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'icon', 'subjects', 'is_active']

    def get_subjects(self, obj):
        return SubjectSerializer(obj.subjects.filter(is_active=True), many=True).data


# ─────────────────────────────────────────────────────────────
# LECTURE
# ─────────────────────────────────────────────────────────────

class LectureVariantSerializer(serializers.ModelSerializer):
    mode_display     = serializers.CharField(source='get_mode_display',     read_only=True)
    language_display = serializers.CharField(source='get_language_display', read_only=True)
    discount_pct     = serializers.SerializerMethodField()

    class Meta:
        model  = LectureVariant
        fields = ['id', 'mode', 'mode_display', 'language', 'language_display',
                  'price', 'original_price', 'discount_pct', 'is_active']

    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return round((1 - float(obj.price) / float(obj.original_price)) * 100)
        return None


class CurriculumItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = LectureCurriculumItem
        fields = ['id', 'title', 'duration', 'order']


class BookMiniSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = ['id', 'title', 'slug', 'image', 'price', 'book_type', 'faculty_name']

    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else ""


class TestSeriesMiniSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model  = TestSeries
        fields = ['id', 'title', 'slug', 'image', 'price',
                  'course_name', 'level', 'test_type', 'faculty_name']

    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else ""


def _faculty_image_url(faculty, request):
    if not faculty or not faculty.image:
        return None
    return request.build_absolute_uri(faculty.image.url) if request else faculty.image.url


class LectureSerializer(serializers.ModelSerializer):
    """Full detail serializer — used for /lectures/<slug>/"""
    category_detail  = CategorySerializer(source='category', read_only=True)
    subject_name     = serializers.CharField(source='subject.name', read_only=True)
    batch_type_display = serializers.CharField(source='get_batch_type_display', read_only=True)
    base_price       = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    variants                = LectureVariantSerializer(many=True, read_only=True)
    curriculum              = CurriculumItemSerializer(many=True, read_only=True)
    recommended_books       = BookMiniSerializer(many=True, read_only=True)
    recommended_test_series = TestSeriesMiniSerializer(many=True, read_only=True)

    # Faculty fields
    faculty_name           = serializers.SerializerMethodField()
    faculty_image          = serializers.SerializerMethodField()
    faculty_bio            = serializers.SerializerMethodField()
    faculty_instagram      = serializers.SerializerMethodField()
    faculty_youtube        = serializers.SerializerMethodField()
    faculty_linkedin       = serializers.SerializerMethodField()
    faculty_subject        = serializers.SerializerMethodField()
    faculty_courses_count  = serializers.SerializerMethodField()
    faculty_students_count = serializers.SerializerMethodField()
    faculty_rating         = serializers.SerializerMethodField()

    class Meta:
        model  = Lecture
        fields = [
            'id', 'title', 'slug', 'image',
            'batch_type', 'batch_type_display',
            'description', 'batch_details',
            'duration', 'total_lectures', 'validity', 'views',
            'is_featured', 'is_active', 'created_at',
            'category', 'category_detail', 'subject', 'subject_name',
            'faculty', 'faculty_name', 'faculty_image', 'faculty_bio',
            'faculty_instagram', 'faculty_youtube', 'faculty_linkedin',
            'faculty_subject', 'faculty_courses_count',
            'faculty_students_count', 'faculty_rating',
            'variants', 'curriculum', 'base_price',
            'recommended_books', 'recommended_test_series',
        ]

    def _f(self, obj): return obj.faculty

    def get_faculty_name(self, obj):           return self._f(obj).name if self._f(obj) else ""
    def get_faculty_image(self, obj):          return _faculty_image_url(self._f(obj), self.context.get('request'))
    def get_faculty_bio(self, obj):            return getattr(self._f(obj), 'bio', '') or ''
    def get_faculty_instagram(self, obj):      return getattr(self._f(obj), 'instagram', '') or ''
    def get_faculty_youtube(self, obj):        return getattr(self._f(obj), 'youtube', '') or ''
    def get_faculty_linkedin(self, obj):       return getattr(self._f(obj), 'linkedin', '') or ''
    def get_faculty_subject(self, obj):        return getattr(self._f(obj), 'subject', '') or ''
    def get_faculty_courses_count(self, obj):
        f = self._f(obj)
        return (getattr(f, 'courses_count', None) or f.lectures.count()) if f else None
    def get_faculty_students_count(self, obj): return getattr(self._f(obj), 'students_count', None)
    def get_faculty_rating(self, obj):         return getattr(self._f(obj), 'rating', None)


class LectureListSerializer(serializers.ModelSerializer):
    """Lightweight — used for listing page & suggested section."""
    category_detail    = CategorySerializer(source='category', read_only=True)
    subject_name       = serializers.CharField(source='subject.name', read_only=True)
    faculty_name       = serializers.SerializerMethodField()
    batch_type_display = serializers.CharField(source='get_batch_type_display', read_only=True)
    base_price         = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    # expose price as alias so the listing page works with either field name
    price              = serializers.DecimalField(source='base_price', max_digits=10, decimal_places=2, read_only=True)
    variant_count      = serializers.SerializerMethodField()

    class Meta:
        model  = Lecture
        fields = [
            'id', 'title', 'slug', 'image',
            'batch_type', 'batch_type_display',
            'base_price', 'price', 'variant_count',
            'validity', 'views', 'is_featured',
            'category_detail', 'subject_name', 'faculty_name',
        ]

    def get_faculty_name(self, obj):  return obj.faculty.name if obj.faculty else ""
    def get_variant_count(self, obj): return obj.variants.filter(is_active=True).count()


# ─────────────────────────────────────────────────────────────
# BOOK
# ─────────────────────────────────────────────────────────────

class BookSerializer(serializers.ModelSerializer):
    category_detail   = CategorySerializer(source='category', read_only=True)
    subject_name      = serializers.CharField(source='subject.name', read_only=True)
    faculty_name      = serializers.SerializerMethodField()
    book_type_display = serializers.CharField(source='get_book_type_display', read_only=True)
    discount_pct      = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = [
            'id', 'title', 'slug', 'image', 'description',
            'book_type', 'book_type_display',
            'price', 'original_price', 'discount_pct',
            'is_active', 'is_featured', 'created_at',
            'faculty', 'faculty_name',
            'category', 'category_detail',
            'subject', 'subject_name',
        ]

    def get_faculty_name(self, obj): return obj.faculty.name if obj.faculty else ""
    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return round((1 - float(obj.price) / float(obj.original_price)) * 100)
        return None


# ─────────────────────────────────────────────────────────────
# TEST SERIES
# ─────────────────────────────────────────────────────────────

class TestSeriesSerializer(serializers.ModelSerializer):
    category_detail    = CategorySerializer(source='category', read_only=True)
    subject_name       = serializers.CharField(source='subject.name', read_only=True)
    faculty_name       = serializers.SerializerMethodField()
    course_name_display = serializers.CharField(source='get_course_name_display', read_only=True)
    level_display      = serializers.CharField(source='get_level_display',        read_only=True)
    test_type_display  = serializers.CharField(source='get_test_type_display',    read_only=True)
    discount_pct       = serializers.SerializerMethodField()

    class Meta:
        model  = TestSeries
        fields = [
            'id', 'title', 'slug', 'image', 'description',
            'course_name', 'course_name_display',
            'level', 'level_display',
            'test_type', 'test_type_display',
            'price', 'original_price', 'discount_pct',
            'total_tests', 'validity',
            'is_active', 'is_featured', 'created_at',
            'faculty', 'faculty_name',
            'category', 'category_detail',
            'subject', 'subject_name',
        ]

    def get_faculty_name(self, obj): return obj.faculty.name if obj.faculty else ""
    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return round((1 - float(obj.price) / float(obj.original_price)) * 100)
        return None


# ─────────────────────────────────────────────────────────────
# COMBO ITEM MINI SERIALIZERS (used inside unified items list)
# ─────────────────────────────────────────────────────────────

class ComboLectureItemSerializer(serializers.ModelSerializer):
    """Lecture inside a combo — includes variants so user can see mode/language options."""
    faculty_name     = serializers.SerializerMethodField()
    subject_name     = serializers.CharField(source='subject.name', read_only=True)
    category_detail  = CategorySerializer(source='category', read_only=True)
    batch_type_display = serializers.CharField(source='get_batch_type_display', read_only=True)
    variants         = LectureVariantSerializer(many=True, read_only=True)
    type             = serializers.SerializerMethodField()
    price            = serializers.DecimalField(source='base_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = Lecture
        fields = [
            'id', 'title', 'slug', 'image', 'type',
            'price', 'original_price',
            'duration', 'total_lectures', 'validity', 'views',
            'faculty_name', 'subject_name', 'category_detail',
            'batch_type_display', 'variants',
        ]

    def get_faculty_name(self, obj): return obj.faculty.name if obj.faculty else ""
    def get_type(self, obj):         return "lecture"


class ComboBookItemSerializer(serializers.ModelSerializer):
    faculty_name      = serializers.SerializerMethodField()
    subject_name      = serializers.CharField(source='subject.name', read_only=True)
    category_detail   = CategorySerializer(source='category', read_only=True)
    book_type_display = serializers.CharField(source='get_book_type_display', read_only=True)
    discount_pct      = serializers.SerializerMethodField()
    type              = serializers.SerializerMethodField()

    class Meta:
        model  = Book
        fields = [
            'id', 'title', 'slug', 'image', 'type',
            'price', 'original_price', 'discount_pct',
            'book_type', 'book_type_display',
            'faculty_name', 'subject_name', 'category_detail',
            'description',
        ]

    def get_faculty_name(self, obj): return obj.faculty.name if obj.faculty else ""
    def get_type(self, obj):         return "book"
    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return round((1 - float(obj.price) / float(obj.original_price)) * 100)
        return None


class ComboTestSeriesItemSerializer(serializers.ModelSerializer):
    faculty_name        = serializers.SerializerMethodField()
    subject_name        = serializers.CharField(source='subject.name', read_only=True)
    category_detail     = CategorySerializer(source='category', read_only=True)
    course_name_display = serializers.CharField(source='get_course_name_display', read_only=True)
    level_display       = serializers.CharField(source='get_level_display',       read_only=True)
    test_type_display   = serializers.CharField(source='get_test_type_display',   read_only=True)
    discount_pct        = serializers.SerializerMethodField()
    type                = serializers.SerializerMethodField()

    class Meta:
        model  = TestSeries
        fields = [
            'id', 'title', 'slug', 'image', 'type',
            'price', 'original_price', 'discount_pct',
            'course_name', 'course_name_display',
            'level', 'level_display',
            'test_type', 'test_type_display',
            'total_tests', 'validity',
            'faculty_name', 'subject_name', 'category_detail',
            'description',
        ]

    def get_faculty_name(self, obj): return obj.faculty.name if obj.faculty else ""
    def get_type(self, obj):         return "test_series"
    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return round((1 - float(obj.price) / float(obj.original_price)) * 100)
        return None


# ─────────────────────────────────────────────────────────────
# COMBO
# ─────────────────────────────────────────────────────────────

class ComboProductSerializer(serializers.ModelSerializer):
    # Unified items list — lectures + books + test_series merged with type field
    items        = serializers.SerializerMethodField()
    savings      = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_pct = serializers.SerializerMethodField()
    price        = serializers.DecimalField(source='combo_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ComboProduct
        fields = [
            'id', 'title', 'slug', 'image', 'description',
            'items',
            'combo_price', 'price', 'original_price', 'savings', 'discount_pct',
            'is_active', 'is_featured', 'created_at',
        ]

    def get_items(self, obj):
        ctx = self.context
        lectures    = ComboLectureItemSerializer(
                        obj.lectures.filter(is_active=True),
                        many=True, context=ctx).data
        books       = ComboBookItemSerializer(
                        obj.books.filter(is_active=True),
                        many=True, context=ctx).data
        test_series = ComboTestSeriesItemSerializer(
                        obj.test_series.filter(is_active=True),
                        many=True, context=ctx).data
        # Return grouped by type so frontend can section them
        return list(lectures) + list(books) + list(test_series)

    def get_discount_pct(self, obj):
        if obj.original_price and obj.original_price > obj.combo_price:
            return round((1 - float(obj.combo_price) / float(obj.original_price)) * 100)
        return None


class ComboProductListSerializer(serializers.ModelSerializer):
    item_count   = serializers.SerializerMethodField()
    savings      = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price        = serializers.DecimalField(source='combo_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = ComboProduct
        fields = ['id', 'title', 'slug', 'image', 'combo_price', 'price',
                  'original_price', 'savings', 'item_count', 'is_featured']

    def get_item_count(self, obj):
        return (obj.lectures.count() + obj.books.count() + obj.test_series.count())