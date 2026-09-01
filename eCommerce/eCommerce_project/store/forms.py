from django import forms
from .models import Store, Product, Review


class StoreForm(forms.ModelForm):
    """Form for creating and editing a store."""
    class Meta:
        model = Store
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Store name'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your store'}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and editing a product."""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': 0}),
        }
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }