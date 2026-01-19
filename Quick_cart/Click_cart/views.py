from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Q

# ✅ Safe PDF import
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None

from .models import (
    Product, CartItem, Order, Bill,
    Category, Wishlist, OrderItem
)

# ===================== HOME =====================

def home(request):
    query = request.GET.get('q')
    trending = request.GET.get('trending')

    products = Product.objects.all()

    if trending == "1":
        products = products.filter(
            category__name__in=[
                "Ovens", "Coolers", "Cameras",
                "Earbuds", "Watches", "Mobiles"
            ]
        )

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'home.html', {
        'products': products,
        'query': query,
        'is_trending': trending == "1"
    })


# ===================== PRODUCT =====================

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


# ===================== CART =====================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart')


@login_required
def cart(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'Click_cart/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def update_quantity(request, id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    return redirect('cart')


@login_required
def remove_from_cart(request, id):
    cart_item = get_object_or_404(CartItem, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart')


# ===================== CHECKOUT =====================

@login_required
def checkout(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)
    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })


@login_required
def place_cart_order(request):
    if request.method == "POST":
        items = CartItem.objects.filter(user=request.user)

        if not items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        total = sum(item.total_price() for item in items)

        order = Order.objects.create(
            user=request.user,
            total=total,
            name=request.POST['name'],
            phone=request.POST['phone'],
            address=request.POST['address']
        )

        Bill.objects.create(order=order)
        items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect('thankyou')

    return redirect('cart')


# ===================== AUTH =====================

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return redirect('register')

        User.objects.create_user(username=username, password=password)
        return redirect('/login/?from_register=1')

    return render(request, 'register.html')


def login_user(request):
    from_register = request.GET.get('from_register') == '1'

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid username or password")
        return redirect('login')

    return render(request, 'login.html', {
        'from_register': from_register
    })


def logout_user(request):
    logout(request)
    request.session.flush()
    return redirect('home')


# ===================== ORDERS =====================

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def bill_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'Click_cart/bill.html', {'order': order})


# ===================== WISHLIST =====================

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })


@login_required
def remove_from_wishlist(request, id):
    Wishlist.objects.filter(id=id, user=request.user).delete()
    return redirect('wishlist')


# ===================== INVOICE PDF =====================

@login_required
def invoice_pdf(request, order_id):
    if not pisa:
        return HttpResponse(
            "PDF feature is currently unavailable.",
            status=503
        )

    order = get_object_or_404(Order, id=order_id)
    template = get_template('Click_cart/invoice_pdf.html')
    html = template.render({'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="invoice_{order.id}.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response