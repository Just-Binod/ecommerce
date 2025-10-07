from django.shortcuts import render,redirect

# from product.models import Product,Category
from product.forms import *
from product.models import  *

from django.contrib import messages


# Create your views here.
def adminhome(request):
    return render(request,'admins/dashboard.html')

def categorylist(request):
    category=Category.objects.all()
    items={
        'category':category
    }

    return render(request,'admins/categorylist.html',items)

def productlist(request):
    product=Product.objects.all()
    items={
        'product':product
    }
    return render(request,'admins/productlist.html',items)




def addproduct(request):
    if request.method== 'POST':
        form=ProductForm(request.POST,  request.FILES)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Product has been added sucessfully ! ')
            return redirect('/admins/addproduct')
        else:
            messages.add_message(request,messages.ERROR,'OOPs, Error occured while adding product ! ')
            return render(request,'admins/addproduct.html',{'form':form})



    forms={
        "form":ProductForm
    }
    return render(request,"admins/addproduct.html",forms)



def addcategory(request):
    if request.method== 'POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Category  has been added sucessfully ! ')
            return redirect('/admins/addcategory')
        else:
            messages.add_message(request,messages.ERROR,'OOPs, Error occured while adding Category ! ')
            return render(request,'admins/addcategory.html',{'form':form})



    forms={
        "form":CategoryForm
    }
    return render(request,"admins/addcategory.html",forms)




