from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    
    # Cart
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),        
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Vendor – Stores
    path('my-stores/', views.my_stores, name='my_stores'),
    path('store/create/', views.create_store, name='create_store'),
    path('store/<int:pk>/edit/', views.edit_store, name='edit_store'),
    path('store/<int:pk>/delete/', views.delete_store, name='delete_store'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<int:store_id>/products/', views.store_product_list, name='store_product_list'),

    # Vendor – Products
    path('my-products/', views.my_products, name='my_products'),
    path('product/create/', views.create_product, name='create_product'),
    path('product/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Vendor
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/<int:vendor_id>/stores/', views.vendor_store_list, name='vendor_store_list'),

    # API Endpoints
    path('api/stores/', views.store_list_create, name='api_store_list_create'),
    path('api/stores/<int:pk>/', views.store_detail, name='api_store_detail'),
    path('api/vendors/<int:vendor_id>/stores/', views.vendor_stores, name='api_vendor_stores'),
    path('api/stores/<int:store_id>/products_list/', views.store_products_list, name='api_store_products'),
    path('api/stores/<int:store_id>/products/', views.store_create_product, name='api_store_products'),
    path('api/products/<int:product_id>/reviews/', views.product_reviews, name='api_product_reviews'),

    # REDDIT third party API
    path('reddit/', views.reddit_feed, name='reddit_feed'),
]

