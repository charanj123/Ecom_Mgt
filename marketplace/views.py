from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
import uuid
import stripe

from .models import Cart, CartItem, Order, OrderItem, Transaction, Wishlist
from .forms import CheckoutForm, QuantityForm
from products.models import Product

# Set up Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def cart_view(request):
    """View to display the user's shopping cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'marketplace/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    """View to add a product to the cart."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            # Check if the product is already in the cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            messages.success(request, f"{product.title} added to your cart.")
            return redirect('marketplace:cart')
    else:
        form = QuantityForm(initial={'product_id': product_id, 'quantity': 1})
    
    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'marketplace/add_to_cart.html', context)


@login_required
def update_cart(request, item_id):
    """View to update the quantity of an item in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, "Cart updated successfully.")
            else:
                cart_item.delete()
                messages.success(request, "Item removed from cart.")
    
    return redirect('marketplace:cart')


@login_required
def remove_from_cart(request, item_id):
    """View to remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('marketplace:cart')


@login_required
def checkout(request):
    """View for the checkout process."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('marketplace:cart')
    
    total_price = cart.get_total_price()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # If user wants to use profile address
            if form.cleaned_data.get('same_as_profile'):
                user = request.user
                form.instance.shipping_address = user.address
                form.instance.shipping_city = user.city
                form.instance.shipping_state = user.state
                form.instance.shipping_country = user.country
                form.instance.shipping_zip_code = user.zip_code
                form.instance.shipping_phone = user.phone_number
            
            # Create order
            order = form.save(commit=False)
            order.buyer = request.user
            order.total_price = total_price
            order.save()
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    seller=cart_item.product.seller,
                    price=cart_item.product.get_final_price(),
                    quantity=cart_item.quantity
                )
            
            # Create payment
            try:
                # Create a Stripe payment intent
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(total_price * 100),  # amount in cents
                    currency='usd',
                    description=f"Order {order.id} payment",
                    metadata={'order_id': order.id}
                )
                
                # Save payment ID to order
                order.payment_id = payment_intent.id
                order.save()
                
                # Clear the cart
                cart.clear()
                
                # Redirect to payment page
                return redirect('marketplace:payment', order_id=order.id)
            
            except Exception as e:
                messages.error(request, f"Payment error: {str(e)}")
                order.delete()
                return redirect('marketplace:checkout')
    else:
        # Pre-fill form with user's profile information
        initial_data = {}
        user = request.user
        if user.address:
            initial_data = {
                'shipping_address': user.address,
                'shipping_city': user.city,
                'shipping_state': user.state,
                'shipping_country': user.country,
                'shipping_zip_code': user.zip_code,
                'shipping_phone': user.phone_number,
            }
        form = CheckoutForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'marketplace/checkout.html', context)


@login_required
def payment(request, order_id):
    """View for handling the payment process."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    context = {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'marketplace/payment.html', context)


@login_required
def payment_success(request, order_id):
    """View for successful payment completion."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Update order status
    order.status = 'processing'
    order.payment_status = 'paid'
    order.save()
    
    # Create transactions for each seller
    for item in order.items.all():
        Transaction.objects.create(
            order=order,
            seller=item.seller,
            buyer=request.user,
            amount=item.get_total_price(),
            status='completed',
            payment_id=order.payment_id,
            transaction_id=f"txn_{uuid.uuid4().hex[:16]}"
        )
    
    messages.success(request, "Payment successful! Your order is being processed.")
    return redirect('marketplace:order_detail', pk=order.id)


@login_required
def payment_cancel(request, order_id):
    """View for cancelled payments."""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # Update order status
    order.status = 'cancelled'
    order.payment_status = 'cancelled'
    order.save()
    
    messages.warning(request, "Payment cancelled. Your order has been cancelled.")
    return redirect('marketplace:orders')


class OrderListView(LoginRequiredMixin, ListView):
    """View to list all orders for the current user."""
    model = Order
    template_name = 'marketplace/order_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """View to show the details of a specific order."""
    model = Order
    template_name = 'marketplace/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        context['items'] = order.items.all()
        return context


@login_required
def sales_list(request):
    """View to list all sales for the current seller."""
    if not request.user.is_seller:
        messages.warning(request, "You are not registered as a seller.")
        return redirect('home')
    
    # Get all order items where the current user is the seller
    sold_items = OrderItem.objects.filter(seller=request.user).order_by('-order__created_at')
    
    # Group sold items by order
    sales_by_order = {}
    for item in sold_items:
        if item.order.id not in sales_by_order:
            sales_by_order[item.order.id] = {
                'order': item.order,
                'items': [],
                'total': 0,
            }
        sales_by_order[item.order.id]['items'].append(item)
        sales_by_order[item.order.id]['total'] += item.get_total_price()
    
    context = {
        'sales': sales_by_order.values(),
    }
    return render(request, 'marketplace/sales_list.html', context)


@login_required
def sale_detail(request, order_id):
    """View to show details of a specific sale."""
    order = get_object_or_404(Order, id=order_id)
    sold_items = OrderItem.objects.filter(order=order, seller=request.user)
    
    if not sold_items.exists():
        messages.error(request, "You don't have any items in this order.")
        return redirect('marketplace:sales_list')
    
    total_sale = sum(item.get_total_price() for item in sold_items)
    
    context = {
        'order': order,
        'items': sold_items,
        'total_sale': total_sale,
    }
    return render(request, 'marketplace/sale_detail.html', context)


@login_required
def update_order_status(request, order_id):
    """View for sellers to update the status of their sold items."""
    order = get_object_or_404(Order, id=order_id)
    sold_items = OrderItem.objects.filter(order=order, seller=request.user)
    
    if not sold_items.exists():
        messages.error(request, "You don't have any items in this order.")
        return redirect('marketplace:sales_list')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        
        if status in valid_statuses:
            # Update the order status - in a real application, you might want to 
            # update individual order items status separately
            order.status = status
            order.save()
            messages.success(request, f"Order status updated to {status}.")
        else:
            messages.error(request, "Invalid status.")
    
    return redirect('marketplace:sale_detail', order_id=order.id)


@login_required
def wishlist(request):
    """View to display the user's wishlist."""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    
    context = {
        'wishlist': wishlist,
        'products': products,
    }
    return render(request, 'marketplace/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """View to add a product to the wishlist."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    wishlist.add_product(product)
    messages.success(request, f"{product.title} added to your wishlist.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('products:product_detail', pk=product_id)


@login_required
def remove_from_wishlist(request, product_id):
    """View to remove a product from the wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    wishlist.remove_product(product)
    messages.success(request, f"{product.title} removed from your wishlist.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    else:
        return redirect('marketplace:wishlist') 