from django.contrib import admin
from .models import Category, Product, ProductImage, ProductRating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'seller', 'product_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'product_type', 'category', 'condition', 'created_at']
    search_fields = ['title', 'description', 'brand', 'seller__username']
    readonly_fields = ['created_at', 'updated_at', 'views']
    list_editable = ['is_active', 'price']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'seller', 'price', 'discount_price', 'is_active', 'is_featured')
        }),
        ('Product Details', {
            'fields': ('product_type', 'condition', 'brand', 'quantity', 'views')
        }),
        ('Location Information', {
            'fields': ('latitude', 'longitude', 'address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'get_product_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    
    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = 'Product Count'


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__title', 'user__username', 'review']
    readonly_fields = ['created_at'] 