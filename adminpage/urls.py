from django.urls import path
from adminpage import views


urlpatterns = [
    path('', views.adminhome, name='admins'),
    path('productlist/', views.productlist, name='productlist'),
    path('categorylist/', views.categorylist, name='categorylist'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('addcategory/', views.addcategory, name='addcategory'),

    

]