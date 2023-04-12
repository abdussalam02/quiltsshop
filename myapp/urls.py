from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    # path('dummy', views.dummy, name='dummy'),

    path('accounts/login/', views.login_user, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_user, name='logout'),

    path('my-profile', views.profile, name='profile'),
    path('remove-address/<str:id>/', views.remove_address, name='remove_address'),
    path('orders', views.user_orders, name='orders'),

    path('products/', views.all_product, name='all_product'),
    path('product/<slug:slug>/', views.product, name='product'),
    path('product/category/<str:cat>/', views.category, name='category'),
    path('search/', views.searched, name="searched"),

    path('review', views.review, name='review'),

    path('my-cart/', views.show_cart, name='cart'),
    path('pluscart/', views.plus_cart, name='plus_cart'),
    path('minuscart/', views.minus_cart, name='minus_cart'),
    path('removecart/<str:id>/', views.remove_cart, name='remove_cart'),
    path('addcart/<str:id>/', views.add_cart, name='addcart'),

    path('my-wishlist', views.wishlist, name='wishlist'),
    path('addwish/<str:id>/', views.addwish, name='addwish'),
    path('removewishlist/<str:id>/', views.remove_wishlist, name='remove_wishlist'),

    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    
    path('blogs', views.blogs, name='blogs'),
    path('blog/<str:slug>', views.blog_details, name='blog_details'),
    path('contact', views.contact, name='contact'),
    path('subscribe', views.subscribe, name='subscribe'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)