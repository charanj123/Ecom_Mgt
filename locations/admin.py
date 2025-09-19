from django.contrib import admin
from .models import Location, UserLocation, StoreLocation


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'city', 'state', 'country', 'created_at']
    list_filter = ['city', 'state', 'country', 'created_at']
    search_fields = ['name', 'address', 'city', 'state', 'country', 'zip_code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ['user', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['timestamp']


@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'address', 'city', 'state', 'is_active']
    list_filter = ['is_active', 'city', 'state', 'country', 'created_at']
    search_fields = ['name', 'seller__username', 'address', 'city', 'state', 'country', 'zip_code']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active'] 