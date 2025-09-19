from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('map/', views.map_view, name='map'),
    path('update-location/', views.update_user_location, name='update_user_location'),
    
    # Store location URLs
    path('stores/', views.StoreLocationListView.as_view(), name='store_list'),
    path('stores/<int:pk>/', views.StoreLocationDetailView.as_view(), name='store_detail'),
    path('stores/create/', views.StoreLocationCreateView.as_view(), name='store_create'),
    path('stores/<int:pk>/update/', views.StoreLocationUpdateView.as_view(), name='store_update'),
    path('stores/<int:pk>/delete/', views.StoreLocationDeleteView.as_view(), name='store_delete'),
] 