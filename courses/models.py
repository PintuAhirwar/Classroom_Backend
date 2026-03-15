from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ─────────────────────────────────────────────────────────────
# SHARED LOOKUP TABLES
# ─────────────────────────────────────────────────────────────

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon name e.g. mdi:web")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="subjects"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────
# LECTURE (Video Product)
# ─────────────────────────────────────────────────────────────

class Lecture(models.Model):
    """
    Core lecture product. Shared content lives here.
    Mode+language+price combinations live in LectureVariant.
    """

    BATCH_TYPE_CHOICES = [
        ("exam_oriented", "Exam Oriented Batch"),
        ("regular", "Regular Batch"),
        ("power", "Power Batch"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    faculty = models.ForeignKey(
        'api.Faculty', on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lectures"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lectures"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="lectures"
    )

    # Batch metadata
    batch_type = models.CharField(max_length=30, choices=BATCH_TYPE_CHOICES, default="regular")

    # Shared content (uploaded once)
    image = models.ImageField(upload_to='lectures/', blank=True, null=True)
    description = models.TextField(blank=True)
    batch_details = models.TextField(blank=True, help_text="HTML rich content for batch details tab")
    duration = models.CharField(max_length=100, blank=True, help_text="e.g. 120 Hours")
    total_lectures = models.PositiveIntegerField(null=True, blank=True)
    validity = models.CharField(max_length=100, blank=True, help_text="e.g. 2 Years")
    views = models.PositiveIntegerField(default=0)

    # Flags
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Recommended products (cross-links to books and test series)
    recommended_books = models.ManyToManyField(
        'Book', blank=True, related_name="recommended_by_lectures"
    )
    recommended_test_series = models.ManyToManyField(
        'TestSeries', blank=True, related_name="recommended_by_lectures"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or f"lecture-{self.pk or 'new'}"
            slug, n = base, 1
            while Lecture.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def base_price(self):
        """Returns the lowest variant price for listing pages."""
        v = self.variants.filter(is_active=True).order_by('price').first()
        return v.price if v else None

    @property
    def original_price(self):
        v = self.variants.filter(is_active=True).order_by('price').first()
        return v.original_price if v else None

    # ── helpers so the detail page works unchanged ──
    @property
    def faculty_name(self):
        return self.faculty.name if self.faculty else ""

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class LectureVariant(models.Model):
    """
    One row per (mode × language) combination for a Lecture.
    Price lives here.
    """

    MODE_CHOICES = [
        ("gd_android_ios", "GD / Android / iOS"),
        ("pendrive", "Pendrive (PD)"),
        ("live", "Live Mode"),
        ("upcoming", "Upcoming Batch"),
    ]

    LANGUAGE_CHOICES = [
        ("hindi", "Hindi"),
        ("english", "English"),
        ("both", "Hindi + English"),
    ]

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="variants")
    mode = models.CharField(max_length=30, choices=MODE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('lecture', 'mode', 'language')
        ordering = ['price']

    def __str__(self):
        return f"{self.lecture.title} — {self.get_mode_display()} / {self.get_language_display()}"


class LectureCurriculumItem(models.Model):
    """Ordered curriculum items for a lecture."""
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="curriculum")
    title = models.CharField(max_length=300)
    duration = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.lecture.title} — {self.title}"


# ─────────────────────────────────────────────────────────────
# BOOK (Hardcopy Product)
# ─────────────────────────────────────────────────────────────

class Book(models.Model):
    BOOK_TYPE_CHOICES = [
        ("concept", "Concept Book"),
        ("question_bank", "Question Bank"),
        ("mcq", "MCQ Book"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    faculty = models.ForeignKey(
        'api.Faculty', on_delete=models.SET_NULL, null=True, blank=True,
        related_name="books"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="books"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="books"
    )
    book_type = models.CharField(max_length=20, choices=BOOK_TYPE_CHOICES, default="concept")
    image = models.ImageField(upload_to='books/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or f"book-{self.pk or 'new'}"
            slug, n = base, 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_book_type_display()})"

    class Meta:
        ordering = ['-created_at']

# ─────────────────────────────────────────────────────────────
# TEST SERIES (Digital Product)
# ─────────────────────────────────────────────────────────────

class TestSeries(models.Model):
    COURSE_CHOICES   = [("ca", "CA"), ("cma", "CMA"), ("other", "Other")]
    LEVEL_CHOICES    = [("final", "Final"), ("inter", "Inter"), ("na", "N/A")]
    TEST_TYPE_CHOICES = [("full", "Full Test"), ("part", "Part Test"), ("full_part", "Full + Part Test")]

    title          = models.CharField(max_length=200)
    slug           = models.SlugField(unique=True, blank=True)
    course_name    = models.CharField(max_length=10, choices=COURSE_CHOICES, default="ca")
    level          = models.CharField(max_length=10, choices=LEVEL_CHOICES,  default="final")
    subject        = models.ForeignKey(Subject,      on_delete=models.SET_NULL, null=True, blank=True, related_name="test_series")
    category       = models.ForeignKey(Category,     on_delete=models.SET_NULL, null=True, blank=True, related_name="test_series")
    faculty        = models.ForeignKey('api.Faculty', on_delete=models.SET_NULL, null=True, blank=True, related_name="test_series")
    test_type      = models.CharField(max_length=15, choices=TEST_TYPE_CHOICES, default="full")
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image          = models.ImageField(upload_to='test_series/', blank=True, null=True)
    description    = models.TextField(blank=True)
    total_tests    = models.PositiveIntegerField(null=True, blank=True)
    validity       = models.CharField(max_length=100, blank=True)
    is_active      = models.BooleanField(default=True)
    is_featured    = models.BooleanField(default=False)
    created_at     = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or f"ts-{self.pk or 'new'}"
            slug, n = base, 1
            while TestSeries.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_course_name_display()} {self.get_level_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Test Series"



# ─────────────────────────────────────────────────────────────
# COMBO PRODUCT
# ─────────────────────────────────────────────────────────────

class ComboProduct(models.Model):
    """
    A combo bundles any mix of Lectures, Books and TestSeries
    into one purchasable package at a combined price.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='combos/', blank=True, null=True)
    description = models.TextField(blank=True)

    # Products included in this combo
    lectures = models.ManyToManyField(Lecture, blank=True, related_name="combos")
    books = models.ManyToManyField(Book, blank=True, related_name="combos")
    test_series = models.ManyToManyField(TestSeries, blank=True, related_name="combos")

    combo_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or f"combo-{self.pk or 'new'}"
            slug, n = base, 1
            while ComboProduct.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def savings(self):
        return (self.original_price - self.combo_price) if self.original_price else 0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']