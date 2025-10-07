from django.db import models

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