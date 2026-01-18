from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Home & Product
    path('', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/<int:id>/', views.update_quantity, name='update_quantity'),

    # Checkout / Order
    path('checkout/', views.checkout, name='checkout'),
    path('place_order/', views.place_cart_order, name='place_order'),
    path('thankyou/', TemplateView.as_view(template_name='thank_you.html'), name='thankyou'),
    path('orders/', views.order_history, name='orders'),
    path('bill/<int:order_id>/', views.bill_view, name='bill'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    # Invoice
    path('invoice/<int:order_id>/', views.invoice_pdf, name='invoice_pdf'),
]