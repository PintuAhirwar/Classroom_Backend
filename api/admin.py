from django.contrib import admin
from .models import Slider, Faculty, Testimonial, Marks, demofile, demolecture
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("id", "email", "name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "is_staff", "is_active")}
        ),
    )
    search_fields = ("email", "name")
    ordering = ("email",)

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'show_search', 'created_at']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'show_search', 'is_active')
        }),
        ('Images', {
            'fields': ('desktop_image', 'mobile_image'),
            'description': 'Desktop: 2400x750px landscape | Mobile: 750x900px portrait'
        }),
    )


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'subject', 'is_active', 'created_at']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']

@admin.register(demofile)
class demofileAdmin(admin.ModelAdmin):
    list_display = ['name', 'book', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']
    raw_id_fields = ['book']

@admin.register(demolecture)
class demolectureAdmin(admin.ModelAdmin):
    list_display = ['title', 'lecture', 'is_active', 'created_at']
    search_fields = ['title']
    list_filter = ['is_active']
    raw_id_fields = ['lecture']