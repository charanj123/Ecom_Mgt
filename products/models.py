from django.db import models
from django.urls import reverse
from users.models import CustomUser


class Category(models.Model):
    """Product category model."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Product model for items being sold on the platform."""
    TYPE_CHOICES = (
        ('physical', 'Physical'),
        ('digital', 'Digital'),
    )
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('not_applicable', 'Not Applicable'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    brand = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})
    
    def get_discount_percentage(self):
        if self.discount_price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount)
        return 0
    
    def get_final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def save(self, *args, **kwargs):
        # Set location based on seller's location if not provided
        if (self.latitude is None or self.longitude is None) and (hasattr(self.seller, 'latitude') and hasattr(self.seller, 'longitude') and self.seller.latitude is not None and self.seller.longitude is not None):
            self.latitude = self.seller.latitude
            self.longitude = self.seller.longitude
        # Set default location if none provided
        elif self.latitude is None or self.longitude is None:
            self.latitude = 0.0
            self.longitude = 0.0
        super().save(*args, **kwargs)
    
    @property
    def main_image(self):
        """Returns the main product image, or the first one if not specified."""
        main_images = self.images.filter(is_main=True)
        if main_images.exists():
            return main_images.first()
        if self.images.exists():
            return self.images.first()
        return None


class ProductImage(models.Model):
    """Model for storing product images."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Image for {self.product.title}"


class ProductRating(models.Model):
    """Model for storing product ratings and reviews."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='product_ratings')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"{self.user.username}'s rating for {self.product.title}: {self.rating}/5" 