from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from .models import Product, Store, Order, OrderItem, Review
from accounts.models import Profile
from .forms import StoreForm, ProductForm, ReviewForm
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .functions.reddit import get_reddit_posts

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
def is_buyer(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'buyer'


def home(request):
    """
    Display the home page with a selection of products.
    """
    products = Product.objects.all()[:12]
    return render(request, 'store/home.html', {'products': products})


def product_list(request):
    """
    Display a list of all available products.
    """
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    form = ReviewForm()

    # Has this user bought the product?
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__buyer=request.user,
            product=product
        ).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
        'has_purchased': has_purchased,
    })
    
@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            has_purchased = OrderItem.objects.filter(
                order__buyer=request.user,
                product=product
            ).exists()

            review, created = Review.objects.get_or_create(
                product=product,
                user=request.user,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment'],
                    'is_verified': has_purchased,
                }
            )

            if not created:
                # User is updating their previous review
                review.rating = form.cleaned_data['rating']
                review.comment = form.cleaned_data['comment']
                review.is_verified = has_purchased
                review.save()
                messages.success(request, 'Your review has been updated.')
            else:
                messages.success(request, 'Review submitted!')

            return redirect('store:product_detail', pk=pk)

    return redirect('store:product_detail', pk=pk)

def is_vendor(user):
    """Check if the logged-in user is a vendor."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.user_type == 'vendor'

def vendor_list(request):
    """List all users who are vendors."""
    vendor_ids = Profile.objects.filter(user_type='vendor').values_list('user_id', flat=True)
    vendors = User.objects.filter(id__in=vendor_ids).order_by('username')
    return render(request, 'store/vendor_list.html', {'vendors': vendors})


def vendor_store_list(request, vendor_id):
    """List stores for one vendor."""
    vendor = get_object_or_404(User, pk=vendor_id)
    stores = Store.objects.filter(owner=vendor)
    return render(request, 'store/vendor_store_list.html', {
        'vendor': vendor,
        'stores': stores,
    })


def store_list(request):
    """List all stores (all vendors)."""
    stores = Store.objects.select_related('owner').all()
    return render(request, 'store/store_list.html', {'stores': stores})


def store_product_list(request, store_id):
    """List products for one store"""
    store = get_object_or_404(Store, pk=store_id)
    products = Product.objects.filter(store=store)
    return render(request, 'store/store_product_list.html', {
        'store': store,
        'products': products,
    })


# ==================== STORE MANAGEMENT ====================

@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def my_stores(request):
    """List all stores owned by the current vendor."""
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'store/my_stores.html', {'stores': stores})


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def create_store(request):
    """Allow a vendor to create a new store."""
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            messages.success(request, 'Store created successfully!')
            return redirect('store:my_stores')
    else:
        form = StoreForm()
    return render(request, 'store/store_form.html', {'form': form, 'title': 'Create Store'})


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def edit_store(request, pk):
    """Allow a vendor to edit one of their own stores."""
    store = get_object_or_404(Store, pk=pk)

    # Permission check – only the owner can edit
    if store.owner != request.user:
        raise PermissionDenied("You do not have permission to edit this store.")

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, 'Store updated successfully!')
            return redirect('store:my_stores')
    else:
        form = StoreForm(instance=store)

    return render(request, 'store/store_form.html', {'form': form, 'title': 'Edit Store'})


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def delete_store(request, pk):
    """Allow a vendor to delete one of their own stores."""
    store = get_object_or_404(Store, pk=pk)

    if store.owner != request.user:
        raise PermissionDenied("You do not have permission to delete this store.")

    if request.method == 'POST':
        store.delete()
        messages.success(request, 'Store deleted successfully!')
        return redirect('store:my_stores')

    return render(request, 'store/store_confirm_delete.html', {'store': store})


# ==================== PRODUCT MANAGEMENT ====================

@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def my_products(request):
    """List all products belonging to the current vendor’s stores."""
    products = Product.objects.filter(store__owner=request.user)
    return render(request, 'store/my_products.html', {'products': products})


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def create_product(request):
    """Allow a vendor to add a new product to one of their stores."""
    # Only show stores owned by this vendor
    stores = Store.objects.filter(owner=request.user)
    if not stores.exists():
        messages.warning(request, 'You need to create a store first before adding products.')
        return redirect('store:create_store')

    # Pre-select chosen store
    selected_store_id = request.GET.get('store')
    # Converting to integer
    if selected_store_id:
        try:
            selected_store_id = int(selected_store_id)
        except (TypeError, ValueError):
            selected_store_id = None
    else:
        selected_store_id = None
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        store_id = request.POST.get('store')
        if form.is_valid() and store_id:
            product = form.save(commit=False)
            product.store = get_object_or_404(Store, id=store_id, owner=request.user)
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('store:my_products')
    else:
        form = ProductForm()

    return render(request, 'store/product_form.html', {
        'form': form,
        'stores': stores,
        'selected_store_id': selected_store_id,
        'title': 'Add Product'
    })


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def edit_product(request, pk):
    """Allow a vendor to edit one of their own products."""
    product = get_object_or_404(Product, pk=pk)

    # Permission check
    if product.store.owner != request.user:
        raise PermissionDenied("You do not have permission to edit this product.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('store:my_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'store/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'product': product
    })


@login_required
@user_passes_test(is_vendor, login_url='accounts:login')
def delete_product(request, pk):
    """Allow a vendor to delete one of their own products."""
    product = get_object_or_404(Product, pk=pk)

    if product.store.owner != request.user:
        raise PermissionDenied("You do not have permission to delete this product.")

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('store:my_products')

    return render(request, 'store/product_confirm_delete.html', {'product': product})

# ==================== CART (Session-based) ====================

@login_required
def add_to_cart(request, product_id):
    """
    Add a product to the user's session-based shopping cart.
    If the product already exists in the cart, increase its quantity.
    """
    if not is_buyer(request.user):
            messages.error(request, 'Only logged-in buyers can add items to their carts.')
            return redirect('store:home')
        
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    # Do not allow more than available stock
    current_qty = cart.get(product_id_str, {}).get('quantity', 0)
    if current_qty + quantity > product.stock:
        messages.error(request, f'Only {product.stock} units available.')
        return redirect('store:product_detail', pk=product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity
        }

    request.session['cart'] = cart
    messages.success(request, f'"{product.name}" added to cart')
    return redirect('store:cart')

@login_required
def view_cart(request):
    """
    Display the contents of the shopping cart and calculate the total.
    """
    if not is_buyer(request.user):
        messages.error(request, 'Only logged-in buyers can view their carts.')
        return redirect('store:home')
    
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    for product_id, item in cart.items():
        price = Decimal(item['price'])
        quantity = item['quantity']
        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            'product_id': product_id,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })
    
@login_required
def update_cart(request, product_id):
    """
    Update the quantity of a product already in the cart.
    """
    if not is_buyer(request.user):
            messages.error(request, 'Only logged-in buyers can update their carts.')
            return redirect('store:home')
    
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            # Treat 0 or negative as "remove"
            if product_id_str in cart:
                del cart[product_id_str]
                messages.info(request, 'Item removed from cart')
        else:
            product = get_object_or_404(Product, id=product_id)

            # Do not allow more than available stock
            if quantity > product.stock:
                messages.error(request, f'Only {product.stock} units available.')
                return redirect('store:cart')

            if product_id_str in cart:
                cart[product_id_str]['quantity'] = quantity
                messages.success(request, 'Cart updated')
            else:
                # Safety – item somehow not in cart
                cart[product_id_str] = {
                    'name': product.name,
                    'price': str(product.price),
                    'quantity': quantity
                }

        request.session['cart'] = cart

    return redirect('store:cart')

@login_required
def remove_from_cart(request, product_id):
    """
    Remove a product completely from the shopping cart.
    """
    if not is_buyer(request.user):
            messages.error(request, 'Only logged-in buyers can update their carts.')
            return redirect('store:home')
    
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.info(request, 'Item removed from cart')

    return redirect('store:cart')

@login_required
def checkout(request):
    """
    Process the checkout:
    - Create an Order and OrderItems
    - Reduce product stock
    - Clear the cart
    - Send an invoice email to the user
    """
    if not is_buyer(request.user):
            messages.error(request, 'Only logged-in buyers checkout.')
            return redirect('store:home')
        
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty')
        return redirect('store:product_list')

    # Validating items in cart
    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        if item['quantity'] > product.stock:
            messages.error(
                request,
                f'Not enough stock for "{product.name}". Available: {product.stock}'
            )
            return redirect('store:cart')
    
    # Calculate total
    total = sum(
        Decimal(item['price']) * item['quantity']
        for item in cart.values()
    )

    # Create the order
    order = Order.objects.create(
        buyer=request.user,
        total=total
    )
    
    # items = OrderItem.objects.filter(order=order)
    order_items_for_email = []
    
    # Create order items and update stock
    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        oi = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=Decimal(item['price'])
        )
        # Reduce stock
        product.stock -= item['quantity']
        product.save()
    
    
        order_items_for_email.append({
            'product': oi.product,
            'quantity': oi.quantity,
            'price': oi.price,
            'subtotal': oi.price * oi.quantity,
        })



    # Clear the cart
    request.session['cart'] = {}

    # Send invoice email (appears in the terminal during development)
    subject=f'Invoice for Order #{order.id}'
    
    message = render_to_string('store/emails/invoice_email.html', {
        'user': request.user,
        'order': order,
        'order_items': order_items_for_email,
    })
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    messages.success(request, 'Order placed successfully! Invoice sent to your email.')
    return redirect('store:home')

# ==================== API VIEWS ====================
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
def store_list_create(request):
    """ 
    GET - list all stores
    POST - create new store (only for logged-in vendor)
    """
    if request.method == 'GET':
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)
    
    # Create Store - POST
    # User needs to be authenticated vendor
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    data = request.data.copy()
    # Set owner to logged-in user
    data['owner'] = request.user.id
    
    serializer = StoreSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def store_detail(request, pk):
    """GET a store via ID"""
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    serializer = StoreSerializer(store)
    return Response(serializer.data)

@api_view(['GET'])
def vendor_stores(request, vendor_id):
    """GET all stores belonging to specific vendor"""
    stores = Store.objects.filter(owner_id=vendor_id)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def store_products_list(request, store_id):
    """ 
    GET - list products of store
    """
    
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    products = store.products.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def store_create_product(request, store_id):
    """ 
    GET - list products of store
    POST - add product to store (only owner vendor)
    """
    
    try:
        store = Store.objects.get(pk=store_id)
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        products = store.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    # Create Product - POST
    # Check if logged-in vendor actually owns store
    if store.owner != request.user:
        return Response(
            {'error': 'You do not own this store.'},
            status=status.HTTP_403_FORBIDDEN
        )
        
    data = request.data.copy()
    # Force correct store
    data['store'] = store.id
    
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_reviews(request, product_id):
    
    """GET all reviews for a product"""
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
    reviews = product.reviews.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# ================= REDDIT =============================

def reddit_feed(request):
    """ 
    Fetch and display reddit posts
    """
    posts = get_reddit_posts("python")
    return render(request, "store/reddit_feed.html", {"posts": posts})