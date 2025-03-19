from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name= "register"),
    path("", views.home_view, name= "home"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("my_orders/download_my_orders_excel", views.download_my_orders_excel, name="download_my_orders_excel"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout_view"),
    path("restaurant/<int:restaurant_id>/menu/", views.main_menu_view, name="main_menu_view"),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/count/', views.cart_count_view, name='cart_count_view'),
    path('cart/payment_gateway', views.payment_gateway, name='payment_gateway'),
    path('cart/checkout/', views.checkout, name="checkout"),
    path('cart/checkout/order_confirmation/<int:order_id>/', views.order_confirmation, name="order_confirmation"),
]