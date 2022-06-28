from django.contrib import admin
from .models import Cart, CartItem

# Register your models here.
class AdminCart(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

class AdminCartItem(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')

admin.site.register(Cart,AdminCart)
admin.site.register(CartItem,AdminCartItem)