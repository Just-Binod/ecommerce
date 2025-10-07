from django.shortcuts import render

from . models import Category, Product

# Create your views here.
def home(request):
    
    return render(request, 'home.html') 


def index(request):
    product=Product.objects.all()
    context={'product':product}
    return render(request, 'ecommerce/index.html',context)

def product(request):
    product=Product.objects.all()
    context={'product':product}
    return render(request, 'ecommerce/product.html',context)