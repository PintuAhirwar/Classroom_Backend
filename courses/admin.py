from django.contrib import admin
from .models import (
    Category, Subject,
    Lecture, LectureVariant, LectureCurriculumItem,
    Book,
    TestSeries,
    ComboProduct,
)


class LectureVariantInline(admin.TabularInline):
    model  = LectureVariant
    extra  = 1
    fields = ['mode', 'language', 'price', 'original_price', 'is_active']


class CurriculumInline(admin.TabularInline):
    model   = LectureCurriculumItem
    extra   = 3
    fields  = ['order', 'title', 'duration']
    ordering = ['order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'icon', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ['name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display        = ['name', 'slug', 'category', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter         = ['category']
    search_fields       = ['name']


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display        = ['title', 'batch_type', 'faculty', 'category', 'subject', 'is_featured', 'is_active', 'created_at']
    list_filter         = ['batch_type', 'is_featured', 'is_active', 'category']
    search_fields       = ['title', 'faculty__name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal   = ['recommended_books', 'recommended_test_series']
    inlines             = [LectureVariantInline, CurriculumInline]
    fieldsets = (
        ('Basic Info',   {'fields': ('title', 'slug', 'faculty', 'category', 'subject', 'batch_type', 'image')}),
        ('Content',      {'fields': ('description', 'batch_details', 'duration', 'total_lectures', 'validity')}),
        ('Settings',     {'fields': ('views', 'is_featured', 'is_active')}),
        ('Recommended',  {'fields': ('recommended_books', 'recommended_test_series')}),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display        = ['title', 'book_type', 'faculty', 'subject', 'price', 'is_featured', 'is_active']
    list_filter         = ['book_type', 'is_featured', 'is_active', 'category']
    search_fields       = ['title', 'faculty__name']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(TestSeries)
class TestSeriesAdmin(admin.ModelAdmin):
    list_display        = ['title', 'course_name', 'level', 'test_type', 'faculty', 'price', 'is_active']
    list_filter         = ['course_name', 'level', 'test_type', 'is_featured', 'is_active']
    search_fields       = ['title', 'faculty__name']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ComboProduct)
class ComboProductAdmin(admin.ModelAdmin):
    list_display      = ['title', 'combo_price', 'original_price', 'is_featured', 'is_active']
    filter_horizontal = ['lectures', 'books', 'test_series']
    search_fields     = ['title']
    prepopulated_fields = {'slug': ('title',)}