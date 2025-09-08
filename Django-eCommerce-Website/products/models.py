# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models import Avg, F # For calculating average rating
from base.models import BaseModel # Assuming BaseModel is in base/models.py

User = get_user_model() # Get the currently active User model

# Define the Category model
class Category(BaseModel): # Inherit from BaseModel for uid, created_at, updated_at
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=200) # For SEO-friendly URLs

    class Meta:
        verbose_name_plural = "Categories" # Correct plural for admin display
        ordering = ['category_name'] # Default ordering

    def save(self, *args, **kwargs):
        # Auto-generate slug from category_name if not provided
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name

# Define the Product model
class Product(BaseModel): # Inherit from BaseModel   #Q6
    product_name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products") # Link to Category
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    stock = models.PositiveIntegerField(default=0) # Current stock level
    
    # --- ADDED: ManyToMany relationships for variants ---
    color_variants = models.ManyToManyField('ColorVariant', blank=True, related_name='products')
    size_variants = models.ManyToManyField('SizeVariant', blank=True, related_name='products')
    # --- END ADDED ---

    class Meta:
        ordering = ['product_name'] # Default ordering

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
    @property
    def average_rating(self):
        """Calculates the average rating for the product based on its reviews."""
        # 'reviews' is the related_name from ProductReview.product
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0

# Define the ProductImage model (one product can have multiple images)
class ProductImage(BaseModel): # Inherit from BaseModel
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")  #Q6
    image = models.ImageField(upload_to="products/images/") # Stores image file

    def __str__(self):
        return f"Image for {self.product.product_name}"

# Define the ColorVariant model (for product variations)
class ColorVariant(BaseModel): # Inherit from BaseModel
    color_name = models.CharField(max_length=100)
    color_code = models.CharField(max_length=7, help_text="Hex color code, e.g., #FF0000") # Hex code for display
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Price impact of this variant

    class Meta:
        verbose_name_plural = "Color Variants"
        ordering = ['color_name']

    def __str__(self):
        return self.color_name

# Define the SizeVariant model (for product variations)
class SizeVariant(BaseModel): # Inherit from BaseModel
    size_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Price impact of this variant

    class Meta:
        verbose_name_plural = "Size Variants"
        ordering = ['size_name']

    def __str__(self):
        return self.size_name

# Define the Coupon model
class Coupon(BaseModel): # Inherit from BaseModel
    coupon_code = models.CharField(max_length=50, unique=True)
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed_amount', 'Fixed Amount'),
    ]
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.coupon_code

# Define the ProductReview model
class ProductReview(BaseModel): # Inherit from BaseModel
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_reviews")
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)]) # Rating from 1 to 5
    comment = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Reviews"
        unique_together = ('product', 'user') # One review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.product_name} ({self.rating} stars)"