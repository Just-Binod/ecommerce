from django.shortcuts import render,redirect

# from product.models import Product,Category
from product.forms import *
from product.models import  *

from django.contrib import messages
from user.auth import *
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
@admin_only
def adminhome(request):
    return render(request,'admins/dashboard.html')


@login_required
@admin_only
def categorylist(request):
    category=Category.objects.all()
    items={
        'category':category
    }

    return render(request,'admins/categorylist.html',items)

@login_required
@admin_only
def productlist(request):
    product=Product.objects.all()
    items={
        'product':product
    }
    return render(request,'admins/productlist.html',items)


@login_required
@admin_only
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


@login_required
@admin_only
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




@login_required
@admin_only
def updateproduct(request,product_id):
    instance=Product.objects.get(id=product_id)
    if request.method== 'POST':
        form=ProductForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Product has been updated sucessfully ! ')
            return redirect('/admins/productlist')
        else:
            messages.add_message(request,messages.ERROR,'OOPs, Error occured while updating product ! ')
            return render(request,'admins/updateproduct.html',{'form':form})
    form=ProductForm(instance=instance)
    return render(request,'admins/updateproduct.html',{'form':form})



@login_required
@admin_only
def updatecategory(request,category_id):
    instance=Category.objects.get(id=category_id)
    if request.method== 'POST':
        form=CategoryForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.add_message(request,messages.SUCCESS,'Category has been updated sucessfully ! ')
            return redirect('/admins/categorylist')
        else:
            messages.add_message(request,messages.ERROR,'OOPs, Error occured while updating Category ! ')
            return render(request,'admins/updatecategory.html',{'form':form})
    form=CategoryForm(instance=instance)
    return render(request,'admins/updatecategory.html',{'form':form})




# @login_required
# @admin_only
# def updateproduct(request,product_id):
#     instance=Product.objects.get(id=product_id)
#     forms={
#         'form':ProductForm(instance=instance)
#     }
#     return render(request,'admins/updateproduct.html',forms)



@login_required
@admin_only
def deleteproduct(request,product_id):
    product=Product.objects.get(id=product_id)
    product.delete()
    messages.add_message(request,messages.SUCCESS,'Product has been deleted sucessfully ! ')
    return redirect('/admins/productlist')


@login_required
@admin_only
def deletecategory(request,category_id):
    category=Category.objects.get(id=category_id)
    category.delete()
    messages.add_message(request,messages.SUCCESS,'Category has been deleted sucessfully ! ')
    return redirect('/admins/categorylist')
