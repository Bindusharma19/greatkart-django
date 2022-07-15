from django.contrib import admin
from .models import Product, Variation

# Register your models here.
class AdminProduct(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'category', 'modified_date', 'is_available', 'stock')
    prepopulated_fields = {'slug':('product_name',)}

class AdminVariation(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')

admin.site.register(Product,AdminProduct)
admin.site.register(Variation,AdminVariation)