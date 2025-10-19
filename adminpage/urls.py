from django.urls import path
from adminpage import views


urlpatterns = [
    path('', views.adminhome, name='admins'),
    path('productlist/', views.productlist, name='productlist'),
    path('categorylist/', views.categorylist, name='categorylist'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('updateproduct/<int:product_id>', views.updateproduct, name='updateproduct'),
    path('addcategory/', views.addcategory, name='addcategory'),
    path('updatecategory/<int:category_id>', views.updatecategory, name='updatecategory'),
    path('deleteproduct/<int:product_id>', views.deleteproduct, name='deleteproduct'),
    path('deletecategory/<int:category_id>', views.deletecategory, name='deletecategory'),
    path('confirm_payment/', views.confirm_payment, name='confirm_payment'),

    #########
    path('user-management/', views.user_management, name='user_management'),
    path('ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    
    #########


]