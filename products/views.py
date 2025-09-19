from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q, Avg, Count
import math

from .models import Product, Category, ProductRating
from .forms import ProductForm, ProductImageFormSet, ProductRatingForm, ProductFilterForm
from users.models import CustomUser


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        
        # Apply search query if provided
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) |
                Q(brand__icontains=q)
            )
        
        # Apply category filter
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                pass
        
        # Apply product type filter
        product_type = self.request.GET.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        # Apply condition filter
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Apply price range filter
        price_range = self.request.GET.get('price_range')
        if price_range:
            try:
                min_price, max_price = price_range.split('-')
                if min_price:
                    queryset = queryset.filter(price__gte=float(min_price))
                if max_price:
                    queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Apply location filter if available
        location = self.request.GET.get('location')
        distance = self.request.GET.get('distance')
        if location and distance:
            # This is a simplified approach; in a real implementation, you'd use a geocoding service
            # to convert the location string to coordinates and calculate distances
            try:
                # For demo, we're just using fixed coordinates (0, 0)
                user_lat = 0.0
                user_lng = 0.0
                distance_miles = int(distance)
                
                # This is a simple implementation without spatial queries
                # In a real app, you'd likely want to use a more efficient approach
                filtered_products = []
                for product in queryset:
                    if product.latitude is not None and product.longitude is not None:
                        # Calculate distance using Haversine formula (simplified)
                        lat_diff = product.latitude - user_lat
                        lng_diff = product.longitude - user_lng
                        distance_approx = math.sqrt(lat_diff**2 + lng_diff**2) * 69  # Rough miles conversion
                        if distance_approx <= distance_miles:
                            product.distance = distance_approx
                            filtered_products.append(product)
                
                # Sort by distance
                filtered_products.sort(key=lambda p: p.distance)
                return filtered_products
            except Exception as e:
                print(f"Error in location filtering: {e}")
        
        # Apply sorting
        sort_by = self.request.GET.get('sort_by', '-created_at')
        valid_sort_fields = ['created_at', '-created_at', 'price', '-price', '-views']
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProductFilterForm(self.request.GET or None)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Increment view count
        product.views += 1
        product.save()
        
        # Add product images to context
        context['images'] = product.images.all()
        
        # Add ratings to context
        context['ratings'] = product.ratings.all().order_by('-created_at')
        context['avg_rating'] = product.ratings.aggregate(Avg('rating'))['rating__avg']
        context['rating_count'] = product.ratings.count()
        
        # Add rating form to context
        context['rating_form'] = ProductRatingForm()
        
        # Check if the user can rate this product
        user = self.request.user
        if user.is_authenticated:
            context['can_rate'] = not product.ratings.filter(user=user).exists() and user != product.seller
        else:
            context['can_rate'] = False
        
        # Get related products (same category)
        context['related_products'] = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:4]
        
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = ProductImageFormSet()
        return context
    
    def form_valid(self, form):
        form.instance.seller = self.request.user
        context = self.get_context_data()
        formset = context['formset']
        
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Product created successfully!')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['formset'] = ProductImageFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, 'Product updated successfully!')
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def test_func(self):
        product = self.get_object()
        return self.request.user == product.seller
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required
def rate_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Users can't rate their own products
    if request.user == product.seller:
        messages.error(request, "You cannot rate your own product.")
        return redirect('products:product_detail', pk=pk)
    
    # Check if user has already rated this product
    if ProductRating.objects.filter(product=product, user=request.user).exists():
        messages.error(request, "You have already rated this product.")
        return redirect('products:product_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProductRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            
            # Update product's average rating
            avg_rating = ProductRating.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            # This would be implemented in a real application
            
            messages.success(request, "Your rating has been submitted successfully!")
        else:
            messages.error(request, "There was an error with your submission.")
    
    return redirect('products:product_detail', pk=pk)


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products')) 