from rest_framework import serializers
from .models import Store, Product, Review

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id','owner', 'name', 'description']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'store', 'name', 'description', 'price', 'stock', 'image']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'comment', 'created_at', 'is_verified']