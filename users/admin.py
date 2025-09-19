from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRating
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_seller', 'seller_rating']
    list_filter = ['is_seller', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Information', {'fields': ('bio', 'phone_number', 'profile_picture',
                                            'location', 'address', 'city', 'state', 
                                            'country', 'zip_code', 'is_seller', 'seller_rating')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Information', {'fields': ('email', 'first_name', 'last_name', 'is_seller')}),
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['username']


class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'rated_by', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'rated_by__username', 'review']
    readonly_fields = ['created_at']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRating, UserRatingAdmin) 