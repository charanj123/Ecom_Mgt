from django.db import models
from users.models import CustomUser
from products.models import Product


class Location(models.Model):
    """Model for storing location data."""
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class UserLocation(models.Model):
    """Model for tracking user location history."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='location_history')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} at {self.timestamp}"


class StoreLocation(models.Model):
    """Model for physical store or pickup locations."""
    name = models.CharField(max_length=255)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='store_locations')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone_number = models.CharField(max_length=20, blank=True)
    business_hours = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name 