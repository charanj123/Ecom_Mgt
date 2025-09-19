from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/location/', views.update_location, name='update_location'),
    path('rate/<int:pk>/', views.rate_user, name='rate_user'),
    path('sellers/', views.SellerListView.as_view(), name='seller_list'),
] 