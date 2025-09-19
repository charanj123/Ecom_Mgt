from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib import messages
from django.db.models import Avg

from .models import CustomUser, UserRating
from .forms import CustomUserChangeForm, UserLocationForm, UserRatingForm
from products.models import Product


class ProfileDetailView(DetailView):
    model = CustomUser
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Add user's products if they are a seller
        if user.is_seller:
            context['products'] = Product.objects.filter(seller=user, is_active=True)
        
        # Add ratings
        context['ratings'] = UserRating.objects.filter(user=user).order_by('-created_at')
        context['rating_form'] = UserRatingForm()
        context['can_rate'] = self.request.user.is_authenticated and self.request.user != user
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/profile_update.html'
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        messages.success(self.request, 'Your profile has been updated.')
        return reverse_lazy('users:profile_detail', kwargs={'pk': self.object.pk})


@login_required
def update_location(request):
    if request.method == 'POST':
        form = UserLocationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your location has been updated.')
            return redirect('users:profile_detail', pk=request.user.pk)
    else:
        form = UserLocationForm(instance=request.user)
    
    return render(request, 'users/update_location.html', {'form': form})


@login_required
def rate_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    
    # Users can't rate themselves
    if request.user == user:
        messages.error(request, "You cannot rate yourself.")
        return redirect('users:profile_detail', pk=pk)
    
    if request.method == 'POST':
        form = UserRatingForm(request.POST)
        if form.is_valid():
            # Check if rating already exists and update it
            rating, created = UserRating.objects.get_or_create(
                user=user,
                rated_by=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'review': form.cleaned_data['review']
                }
            )
            
            if not created:
                rating.rating = form.cleaned_data['rating']
                rating.review = form.cleaned_data['review']
                rating.save()
            
            # Update user's average rating
            avg_rating = UserRating.objects.filter(user=user).aggregate(Avg('rating'))['rating__avg']
            user.seller_rating = avg_rating
            user.save()
            
            messages.success(request, f"You have rated {user.username} successfully.")
        else:
            messages.error(request, "There was an error with your submission.")
    
    return redirect('users:profile_detail', pk=pk)


class SellerListView(ListView):
    model = CustomUser
    template_name = 'users/seller_list.html'
    context_object_name = 'sellers'
    
    def get_queryset(self):
        return CustomUser.objects.filter(is_seller=True).order_by('-seller_rating') 