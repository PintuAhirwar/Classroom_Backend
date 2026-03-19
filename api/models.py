from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import AbstractUser
import random
from courses.models import Lecture, Book


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
    desktop_image = models.ImageField(upload_to='slider/desktop/', null=True, blank=True)
    mobile_image = models.ImageField(upload_to='slider/mobile/', null=True, blank=True)
    show_search = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
 
    def __str__(self):
        return self.title
 
 
class FloatingCard(models.Model):
    """
    5 fixed-position floating cards for the hero banner (show_search=True slider).
 
    Position map (matches FloatingCards.jsx):
        0 → Top Center-Left   (e.g. Reliance)
        1 → Top Right         (e.g. L&T)
        2 → Middle Left       (e.g. ICICI Bank)
        3 → Middle Right      (e.g. TCS)
        4 → Bottom Left       (e.g. Accenture)
    """
    POSITION_CHOICES = [
        (0, 'Top Center-Left'),
        (1, 'Top Right'),
        (2, 'Middle Left'),
        (3, 'Middle Right'),
        (4, 'Bottom Left'),
    ]
 
    slider = models.ForeignKey(
        Slider,
        on_delete=models.CASCADE,
        related_name='floating_cards'
    )
    label = models.CharField(max_length=80, help_text="Main text, e.g. Reliance Industries")
    sub_label = models.CharField(max_length=80, blank=True, help_text="Optional second line")
    icon = models.CharField(max_length=100, help_text="Iconify icon name, e.g. mdi:bank")
    icon_color = models.CharField(max_length=20, default='#2563eb')
    bg_color = models.CharField(max_length=20, default='#ffffff')
    position_index = models.PositiveSmallIntegerField(
        choices=POSITION_CHOICES,
        default=0,
        help_text="0=Top-CenterLeft | 1=Top-Right | 2=Mid-Left | 3=Mid-Right | 4=Bottom-Left"
    )
    is_active = models.BooleanField(default=True)
 
    class Meta:
        ordering = ['position_index']
        unique_together = [['slider', 'position_index']]
 
    def __str__(self):
        return f"{self.slider.title} — {self.label} (pos {self.position_index})"
    
    
class Faculty(models.Model):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    image = models.ImageField(upload_to='faculty/')

    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

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
    
    book = models.ForeignKey(
        Book, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="demo_files"
    )

    def __str__(self):
        return self.name

class demolecture(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    lecture = models.ForeignKey(
        Lecture, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="demo_lectures"
    )

    def __str__(self):
        return self.title

class Enquiry(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20)
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"