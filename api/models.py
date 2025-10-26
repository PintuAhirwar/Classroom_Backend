from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser
import random

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    
    # Allow null/blank for phone to avoid UNIQUE constraint errors
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    address = models.TextField(blank=True, default="")
    bio = models.TextField(blank=True, default="")
    dob = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Required fields for Django admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone']
    
    def generate_otp(self):
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        self.save()
        return otp

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email



class Slider(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='slider/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class Course(models.Model):
    title = models.CharField(max_length=200)
    faculty = models.CharField(max_length=50)
    image = models.ImageField(upload_to='course/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
    
class Faculty(models.Model):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    social_media = models.URLField(max_length=200, blank=True)
    image = models.ImageField(upload_to='faculty/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    feedback = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True)
    course = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
class Marks(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='marks/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class demofile(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='demo_images/', blank=True)
    urls = models.URLField(max_length=300, default="", blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class demolecture(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title