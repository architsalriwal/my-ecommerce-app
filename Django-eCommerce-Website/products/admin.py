# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\products\admin.py

from django.contrib import admin
# Removed Wishlist from the import statement
from .models import Category, Product, ProductImage, ColorVariant, SizeVariant, Coupon, ProductReview
from django.utils.html import format_html # Import this for rendering HTML safely

# Admin for Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'slug'] # Removed 'category_image' as it's not in the model you provided earlier
    prepopulated_fields = {'slug': ('category_name',)}
    search_fields = ['category_name']

# Inline for Product Images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Number of empty forms to display
    fields = ('image', 'img_preview') # Display the image field and the preview
    readonly_fields = ('img_preview',) # Make the preview read-only

    # Define the img_preview method here
    def img_preview(self, obj):
        if obj.image: # Check if an image exists
            # Use format_html to render a safe HTML img tag
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "(No Image)"
    img_preview.short_description = "Image Preview" # This sets the column header in the admin

# Admin for Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Removed 'newest_product' as it's not in the Product model you provided earlier
    # Also removed 'available' as it's not in the Product model
    list_display = ['product_name', 'category', 'price', 'stock'] 
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductImageInline] # Add the inline for images
    # Removed 'available' and 'newest_product' from list_filter and list_editable
    list_filter = ['category'] 
    list_editable = ['price', 'stock'] 
    # Corrected typo: 'product_desription' to 'product_description'
    search_fields = ['product_name', 'product_description'] 
    raw_id_fields = ('category',) # Can be useful for large number of categories

# Admin for ColorVariant
@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']
    search_fields = ['color_name']

# Admin for SizeVariant
@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    # Removed 'order' as it's not in the SizeVariant model you provided earlier
    list_display = ['size_name', 'price']
    list_editable = ['price'] # Removed 'order'
    search_fields = ['size_name']

# Admin for Coupon
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    # Removed 'is_expired' from list_display and list_filter, assuming you'll manage expiry via expiry_date
    list_display = ['coupon_code', 'discount_amount', 'minimum_amount', 'is_active', 'expiry_date']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['coupon_code']
    list_editable = ['discount_amount', 'minimum_amount', 'is_active'] # Changed from is_expired to is_active

# Admin for ProductReview
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    # Changed 'stars' to 'rating' to match the model field name
    # Changed 'date_added' to 'created_at' to match BaseModel field name
    # Changed 'content' to 'comment' to match the model field name
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__product_name', 'user__username', 'comment']
    raw_id_fields = ('user', 'product',) # Useful for linking to users/products

# Removed the entire WishlistAdmin block
# @admin.register(Wishlist)
# class WishlistAdmin(admin.ModelAdmin):
#     list_display = ['user', 'product', 'size_variant']
#     search_fields = ['user__username', 'product__product_name']
#     raw_id_fields = ('user', 'product', 'size_variant',)