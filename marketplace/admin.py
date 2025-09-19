from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, Transaction, Wishlist


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_total_price', 'get_item_count', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'seller', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['buyer__username', 'buyer__email', 'shipping_address']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Information', {
            'fields': ('buyer', 'status', 'total_price', 'payment_id', 'payment_status')
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_country', 'shipping_zip_code', 'shipping_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'seller', 'buyer', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['transaction_id', 'payment_id', 'seller__username', 'buyer__username']
    readonly_fields = ['created_at', 'updated_at']


class WishlistItemInline(admin.TabularInline):
    model = Wishlist.products.through
    extra = 1
    verbose_name = 'Wishlist Item'
    verbose_name_plural = 'Wishlist Items'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WishlistItemInline]
    exclude = ['products'] 