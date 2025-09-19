from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
import json
import math

from .models import Location, UserLocation, StoreLocation
from .forms import LocationForm, StoreLocationForm, LocationSearchForm
from products.models import Product
from users.models import CustomUser


def map_view(request):
    """View to display the main map with products and stores."""
    form = LocationSearchForm(request.GET or None)
    
    # Default center of map if no search
    center_lat = 40.7128  # New York City
    center_lng = -74.0060
    zoom_level = 4
    
    # Get featured products for display
    products = Product.objects.filter(is_active=True, is_featured=True)
    stores = StoreLocation.objects.filter(is_active=True)
    
    if form.is_valid():
        # Get search parameters
        distance_miles = int(form.cleaned_data.get('distance'))
        
        # Use provided coordinates or geocode the address
        latitude = form.cleaned_data.get('latitude')
        longitude = form.cleaned_data.get('longitude')
        
        if latitude and longitude:
            center_lat = latitude
            center_lng = longitude
            zoom_level = 10
            
            # Calculate and filter products by distance
            filtered_products = []
            for product in Product.objects.filter(is_active=True):
                if product.latitude is not None and product.longitude is not None:
                    # Calculate distance using Haversine formula (simplified)
                    lat_diff = product.latitude - latitude
                    lng_diff = product.longitude - longitude
                    distance_approx = math.sqrt(lat_diff**2 + lng_diff**2) * 69  # Rough miles conversion
                    if distance_approx <= distance_miles:
                        product.distance = distance_approx
                        filtered_products.append(product)
            
            # Sort by distance
            filtered_products.sort(key=lambda p: p.distance)
            products = filtered_products
            
            # Calculate and filter stores by distance
            filtered_stores = []
            for store in StoreLocation.objects.filter(is_active=True):
                if store.latitude is not None and store.longitude is not None:
                    # Calculate distance using Haversine formula (simplified)
                    lat_diff = store.latitude - latitude
                    lng_diff = store.longitude - longitude
                    distance_approx = math.sqrt(lat_diff**2 + lng_diff**2) * 69  # Rough miles conversion
                    if distance_approx <= distance_miles:
                        store.distance = distance_approx
                        filtered_stores.append(store)
            
            # Sort by distance
            filtered_stores.sort(key=lambda s: s.distance)
            stores = filtered_stores
    
    # Prepare GeoJSON for products
    products_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [product.longitude, product.latitude]
                },
                "properties": {
                    "id": product.id,
                    "title": product.title,
                    "price": str(product.get_final_price()),
                    "type": product.product_type,
                    "url": reverse_lazy('products:product_detail', kwargs={'pk': product.id})
                }
            }
            for product in products if product.latitude and product.longitude
        ]
    }
    
    # Prepare GeoJSON for stores
    stores_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [store.longitude, store.latitude]
                },
                "properties": {
                    "id": store.id,
                    "name": store.name,
                    "address": store.address,
                    "city": f"{store.city}, {store.state}",
                    "seller": store.seller.username,
                    "seller_url": reverse_lazy('users:profile_detail', kwargs={'pk': store.seller.id})
                }
            }
            for store in stores
        ]
    }
    
    context = {
        'form': form,
        'center_lat': center_lat,
        'center_lng': center_lng,
        'zoom_level': zoom_level,
        'products_geojson': json.dumps(products_geojson),
        'stores_geojson': json.dumps(stores_geojson),
        'products': products[:10],  # Limit for sidebar display
        'stores': stores[:10],  # Limit for sidebar display
    }
    return render(request, 'locations/map.html', context)


@login_required
def update_user_location(request):
    """AJAX view to update a user's current location."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            if latitude and longitude:
                # Update user's location
                user = request.user
                user.latitude = float(latitude)
                user.longitude = float(longitude)
                user.save()
                
                # Create a user location history entry
                UserLocation.objects.create(
                    user=user,
                    latitude=float(latitude),
                    longitude=float(longitude)
                )
                
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Coordinates required'}, status=400)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


class StoreLocationListView(ListView):
    """View to list all store locations."""
    model = StoreLocation
    template_name = 'locations/store_list.html'
    context_object_name = 'stores'
    
    def get_queryset(self):
        return StoreLocation.objects.filter(is_active=True).order_by('name')


class StoreLocationDetailView(DetailView):
    """View to show details of a store location."""
    model = StoreLocation
    template_name = 'locations/store_detail.html'
    context_object_name = 'store'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store = self.get_object()
        
        # Get products from this seller
        context['products'] = Product.objects.filter(
            seller=store.seller,
            is_active=True
        ).order_by('-created_at')
        
        return context


class StoreLocationCreateView(LoginRequiredMixin, CreateView):
    """View to create a new store location."""
    model = StoreLocation
    form_class = StoreLocationForm
    template_name = 'locations/store_form.html'
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        messages.success(self.request, "Store location created successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('locations:store_detail', kwargs={'pk': self.object.pk})


class StoreLocationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View to update a store location."""
    model = StoreLocation
    form_class = StoreLocationForm
    template_name = 'locations/store_form.html'
    
    def test_func(self):
        store = self.get_object()
        return self.request.user == store.seller
    
    def form_valid(self, form):
        messages.success(self.request, "Store location updated successfully.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('locations:store_detail', kwargs={'pk': self.object.pk})


class StoreLocationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View to delete a store location."""
    model = StoreLocation
    template_name = 'locations/store_confirm_delete.html'
    success_url = reverse_lazy('locations:store_list')
    
    def test_func(self):
        store = self.get_object()
        return self.request.user == store.seller
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Store location deleted successfully.")
        return super().delete(request, *args, **kwargs) 