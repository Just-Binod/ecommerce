from django.urls import path
from user import views

urlpatterns = [

    path('', views.homepage, name='homepage'),
    path('productpage/', views.productpage, name='productpage'),
    path('productdetail/<int:product_id>/', views.productdetail, name='productdetail'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
  
    # path('addcategory/', views.addcategory, name='addcategory'),

    

]

