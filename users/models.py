from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model that extends Django's AbstractUser."""
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True, default=0.0)
    longitude = models.FloatField(null=True, blank=True, default=0.0)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    is_seller = models.BooleanField(default=False)
    seller_rating = models.FloatField(default=0.0)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        # Set default location if none provided
        if self.latitude is None or self.longitude is None:
            self.latitude = 0.0
            self.longitude = 0.0
        super().save(*args, **kwargs)


class UserRating(models.Model):
    """Model for storing user ratings."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings_received')
    rated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings_given')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'rated_by']
    
    def __str__(self):
        return f"{self.rated_by.username} rated {self.user.username}: {self.rating}/5" 