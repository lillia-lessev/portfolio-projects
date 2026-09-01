from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Store(models.Model):
    """
    Model representing a store with products

    Fields:
        - name: CharField for the store's name.
        - description: TextField for the store description
        - owner: the vendor who owns the store

    Methods:
        - __str__: Returns a string representation of the store, showing the name

    :param models.Model: Django's base model class.
    """
    # The name of the store
    name = models.CharField(max_length=100)  
    
    # A description of the store; it’s optional (can be empty)
    description = models.TextField(blank=True)  
    
    # The vendor who owns the store
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stores',
        help_text="The vendor who owns the store"
    )
    
    def __str__(self):
        # This makes it easier to see the store’s name when printing or in admin pages
        return self.name

    class Meta:
        # These are special permissions for users who can add, change, delete, or view stores
        permissions = [
            ("add_stores", "Can add stores"),
            ("edit_stores", "Can edit stores"),
            ("delete_stores", "Can delete stores"),
            ("view_stores", "Can view stores"),
        ]
        
class Product(models.Model):
    """
    Model representing a product 

    Fields:
        - name: CharField for the product's name.
        - description: TextField for the product description
        - price: DecimalField for the product's price
        - stock: PositiveIntegerField for the amount of products in stock

    Methods:
        - __str__: Returns a string representation of the product, showing the name

    :param models.Model: Django's base model class.
    """
    # The name of the product
    name = models.CharField(max_length=100)  
    
    # A description of the product; it’s optional (can be empty)
    description = models.TextField(blank=True)  
    
    # The price of the product, with up to 10 digits total and 2 decimal places for cents
    price = models.DecimalField(max_digits=10, decimal_places=2)  
    
    # How many items are available in stock (only positive numbers allowed)
    stock = models.PositiveIntegerField()  
    
    # Product image
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Product image"
    )
    
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The store this product belongs to"
    )
    
    def __str__(self):
        # This makes it easier to see the product’s name when printing or in admin pages
        return self.name

    class Meta:
        # These are special permissions for users who can add, change, delete, or view products
        permissions = [
            ("add_products", "Can add products"),
            ("edit_products", "Can edit products"),
            ("delete_products", "Can delete products"),
            ("view_products", "Can view products"),
        ]


class Order(models.Model):
    """
    Represents a full order / purchase made by a buyer
    """
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_paid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.buyer.username}"

class OrderItem(models.Model):
    """
    Represents a single product line inside an Order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price at the time of purchase"
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,                    # django.contrib.auth.models.User
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="True if the user has purchased this product"
    )

    class Meta:
        unique_together = ('product', 'user')   # one review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} – {self.product.name} ({self.rating}★)'
    
# class User(models.Model):
#     """
#     Model representing a user

#     Fields:
#         - username: CharField for the user's username on the application.
#         - name: CharField for the user's name
#         - email: TextField for the user's email address

#     Methods:
#         - __str__: Returns a string representation of the user, showing the name

#     :param models.Model: Django's base model class.
#     """

#     # Username of user
#     username = models.CharField(max_length=255)
    
#     # User's name
#     name = models.CharField(max_length=255)
    
#     # User's email address
#     email = models.TextField(max_length=255)

#     def __str__(self):
#         return self.name
    
#     class Meta:
#             # These are special permissions for users who can add, change, delete, or view users
#             permissions = [
#                 ("add_users", "Can add users"),
#                 ("edit_users", "Can edit users"),
#                 ("delete_users", "Can delete users"),
#                 ("view_users", "Can view users"),
#             ]