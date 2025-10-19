from django.db import models
from django.contrib.auth.models import User
# Create your models here.

##############################################################

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     is_banned = models.BooleanField(default=False)
#     banned_until = models.DateTimeField(null=True, blank=True)
#     ban_reason = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.user.username} - {'Banned' if self.is_banned else 'Active'}"

# # Signal to create UserProfile when User is created
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'userprofile'):
#         instance.userprofile.save()



# Add this at the end of your models.py file
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Banned' if self.is_banned else 'Active'}"

# Signal to automatically create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
######################################################



class Category(models.Model):
    category_name= models.CharField(max_length=100,unique=True)
    created_at= models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True,null=True)


    def __str__(self):
        return self.category_name





class Product(models.Model):
    product_name= models.CharField(max_length=150)
    product_price= models.FloatField()
    description= models.TextField()
    quantity= models.IntegerField()
    image=models.FileField(upload_to='uploads/products/',null=True)
    category= models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at= models.DateTimeField(auto_now_add=True,null=True)
    uploaded_at= models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return self.product_name



# models.py
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Added quantity field
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.product.product_name

    def total_price(self):
        return self.quantity * self.product.product_price
    


class Order(models.Model):
    PAYMENT_METHOD=(
        ('Cash On Delivery','Cash On Delivery'),
        ('Esewa','Esewa'),
       
    )
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    address= models.CharField(max_length=300)
    total_price=models.IntegerField()
    payment_method= models.CharField(max_length=200, choices=PAYMENT_METHOD) 
    contact_no= models.CharField(max_length=15)
    email=models.EmailField(max_length=100)
    payment_status= models.CharField(default='Pending', max_length=100)
    created_at= models.DateTimeField(auto_now_add=True,null=True)
    updated_at= models.DateTimeField(auto_now=True,null=True)


    def __str__(self):
        return self.product.product_name