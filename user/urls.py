from django.urls import path
from user import views

urlpatterns = [

    path('', views.homepage, name='homepage'),
    path('productpage/', views.productpage, name='productpage'),
    path('productdetail/<int:product_id>/', views.productdetail, name='productdetail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('add_to_cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
    path('cartlist/', views.cartlist, name='cartlist'),
    path('cart/update/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    #

  
    # path('addcategory/', views.addcategory, name='addcategory'),

    

]

