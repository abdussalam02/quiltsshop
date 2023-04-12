from django.contrib import admin
from .models import Information, Carousal, Offer, Product, ProductVariant, Payment, Image, Blog, BlogDetail, Cart, Order, User, Review, Addres, Wishlist, Subscription

class ImageAdmin(admin.StackedInline):
    model = Image

class VariantAdmin(admin.StackedInline):
    model = ProductVariant
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageAdmin, VariantAdmin]

    class Meta:
       model = Product

class DetailAdmin(admin.StackedInline):
    model = BlogDetail
 
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = [DetailAdmin]

    class Meta:
       model = Blog

admin.site.register(Payment)
admin.site.register(Information)
admin.site.register(Carousal)
admin.site.register(Offer)
admin.site.register(User)
admin.site.register(Addres)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Wishlist)
admin.site.register(Subscription)