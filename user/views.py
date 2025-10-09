from django.shortcuts import render,redirect
from product.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .filters import *
from django.contrib.auth import authenticate, login as auth_login, logout 
from user.forms import *
# Create your views here.


def register(request):
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,'User account has been created Sucessfully ! .')
            return redirect('/register')
        else:
             messages.add_message(request, messages.ERROR,' Please provide correct credentials !.')
             return render(request,'user/register.html',{'form':form})

    context={
        'form':UserCreationForm
    }
    return render(request,'user/register.html',context)



def login(request):
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
        user=authenticate(request,username=data['username'],password=data['password'])
        if user is not None:
            auth_login(request,user)
            return redirect('/')
        else:
            messages.add_message(request, messages.ERROR,' OOPs, either username or password is INVALID !.')
            return render(request,'user/loginform.html',{'form':form})
        
    context={
        'form':LoginForm
    }
    return render(request,'user/loginform.html',context)
    
    


def homepage(request):
    product=Product.objects.all().order_by('-id')[:4]
    data={
        'product':product
    }

    return render(request,'user/homepage.html',data)



def productpage(request):
    product=Product.objects.all().order_by('-id')
    product_filter=ProductFilter(request.GET,queryset=product)
    product_final=product_filter.qs
    data={
        'product':product_final,
        'product_filter':product_filter
    }

    return render(request,'user/productpage.html',data)


def productdetail(request,product_id):
    product=Product.objects.get(id=product_id)
    data={
        'product':product
    }

    return render(request,'user/productdetail.html',data)


