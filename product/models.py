from django.db import models
from django.contrib.auth.models import User
# Create your models here.










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
        ('khalthi','khalthi '),
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