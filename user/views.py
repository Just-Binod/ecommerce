from django.shortcuts import render,redirect
from product.models import Cart, Product, Order
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .filters import *
from django.contrib.auth import authenticate, login as auth_login, logout 
from user.forms import *
from django.contrib.auth.decorators import login_required

# from adminpage.views import adminhome
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
            if user.is_staff:
                return redirect('admins')
            else:
                return redirect('/')
        else:
            messages.add_message(request, messages.ERROR,' OOPs, either username or password is INVALID !.')
            return render(request,'user/loginform.html',{'form':form})
        
    context={
        'form':LoginForm
    }
    return render(request,'user/loginform.html',context)
    
    

def logoutuser(request):
    logout(request)
    return redirect('/login')



def homepage(request):
    product=Product.objects.all().order_by('-id')[:4]
    data={
        'product':product
    }

    return render(request,'user/homepage.html',data)


@login_required
def productpage(request):
    product=Product.objects.all().order_by('-id')
    product_filter=ProductFilter(request.GET,queryset=product)
    product_final=product_filter.qs
    data={
        'product':product_final,
        'product_filter':product_filter
    }

    return render(request,'user/productpage.html',data)

@login_required
def productdetail(request,product_id):
    product=Product.objects.get(id=product_id)
    data={
        'product':product
    }

    return render(request,'user/productdetail.html',data)

@login_required
def add_to_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    user=request.user
    check_items=Cart.objects.filter(product=product,user=user)
    if check_items:
        messages.add_message(request,messages.ERROR,'Product already in cart ! ')
        return redirect('/productpage')
    else:
        Cart.objects.create(product=product,user=user)
        messages.add_message(request,messages.SUCCESS,'Product has been added to cart ! ')
        return redirect('/productpage')
    
@login_required
def cart_list(request):
    # product=Product.objects.get(id=product_id)
    user=request.user
    items=Cart.objects.filter(user=user)
    data={
        'items':items
    }
    return render(request,'user/cart.html',data)




# 
# 
# 
# ecommerce/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Sum

# Cart List View
# @login_required
# def cartlist(request):
#     cart_items = Cart.objects.filter(user=request.user).select_related('product')
#     cart_count = cart_items.count()
#     cart_subtotal = sum(item.quantity * item.product.product_price for item in cart_items)

#     context = {
#         'items': cart_items,
#         'cart_count': cart_count,
#         'cart_subtotal': cart_subtotal,
#     }
#     return render(request, 'cart.html', context)

# # Get Cart Count (for AJAX updates in navbar)
# @login_required
# def get_cart_count(request):
#     cart_count = Cart.objects.filter(user=request.user).count()
#     return JsonResponse({'cart_count': cart_count})

# # Update Cart Quantity (AJAX)
# @require_POST
# @login_required
# def update_quantity(request, product_id):
#     try:
#         cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
#         action = request.POST.get('action')
#         if action == 'increase':
#             cart_item.quantity += 1
#         elif action == 'decrease' and cart_item.quantity > 1:
#             cart_item.quantity -= 1
#         cart_item.save()
#         return JsonResponse({
#             'success': True,
#             'quantity': cart_item.quantity,
#             'total_price': cart_item.quantity * cart_item.product.product_price,
#             'cart_subtotal': sum(item.quantity * item.product.product_price for item in Cart.objects.filter(user=request.user))
#         })
#     except:
#         return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# # Remove Item from Cart
# @login_required
# def remove_from_cart(request, product_id):
#     cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
#     cart_item.delete()
#     messages.success(request, f"{cart_item.product.product_name} removed from cart.")
#     return redirect('cartlist')

# # Clear Cart
# @login_required
# def clear_cart(request):
#     Cart.objects.filter(user=request.user).delete()
#     messages.success(request, "Your cart has been cleared.")
#     return redirect('cartlist')

# # Checkout View
# @login_required
# def checkout(request):
#     if request.method == 'POST':
#         # Process form data
#         address = request.POST.get('address')
#         contact_no = request.POST.get('contact_no')
#         email = request.POST.get('email')
#         payment_method = request.POST.get('payment_method')

#         # Validate form data
#         if not all([address, contact_no, email, payment_method]):
#             messages.error(request, "Please fill in all required fields.")
#             return redirect('checkout')

#         # Get cart items
#         cart_items = Cart.objects.filter(user=request.user).select_related('product')
#         if not cart_items:
#             messages.error(request, "Your cart is empty.")
#             return redirect('cartlist')

#         # Create orders
#         for item in cart_items:
#             Order.objects.create(
#                 user=request.user,
#                 product=item.product,
#                 quantity=item.quantity,
#                 address=address,
#                 total_price=item.quantity * item.product.product_price,
#                 payment_method=payment_method,
#                 contact_no=contact_no,
#                 email=email,
#                 payment_status='Pending'
#             )

#         # Clear cart after order creation
#         cart_items.delete()
#         messages.success(request, "Your order has been placed successfully!")
#         return redirect('order_confirmation')  # Adjust to your confirmation page

#     # GET request: Display checkout form
#     cart_items = Cart.objects.filter(user=request.user).select_related('product')
#     cart_subtotal = sum(item.quantity * item.product.product_price for item in cart_items)
#     context = {
#         'items': cart_items,
#         'cart_count': cart_items.count(),
#         'cart_subtotal': cart_subtotal,
#     }
#     return render(request, 'checkout.html', context)



###
# New views for cart.html
@login_required
def cartlist(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    cart_count = cart_items.count()
    cart_subtotal = sum(item.quantity * item.product.product_price for item in cart_items)

    context = {
        'items': cart_items,
        'cart_count': cart_count,
        'cart_subtotal': cart_subtotal,
    }
    return render(request, 'user/cart.html', context)

@login_required
def get_cart_count(request):
    cart_count = Cart.objects.filter(user=request.user).count()
    return JsonResponse({'cart_count': cart_count})

@require_POST
@login_required
def update_quantity(request, product_id):
    try:
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'total_price': cart_item.quantity * cart_item.product.product_price,
            'cart_subtotal': sum(item.quantity * item.product.product_price for item in Cart.objects.filter(user=request.user))
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.product_name} removed from cart.")
    return redirect('cartlist')

@login_required
def clear_cart(request):
    Cart.objects.filter(user=request.user).delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect('cartlist')

@login_required
def checkout(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        contact_no = request.POST.get('contact_no')
        email = request.POST.get('email')
        payment_method = request.POST.get('payment_method')

        if not all([address, contact_no, email, payment_method]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('checkout')

        cart_items = Cart.objects.filter(user=request.user).select_related('product')
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('cartlist')

        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                address=address,
                total_price=item.quantity * item.product.product_price,
                payment_method=payment_method,
                contact_no=contact_no,
                email=email,
                payment_status='Pending'
            )

        cart_items.delete()
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation')

    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    cart_subtotal = sum(item.quantity * item.product.product_price for item in cart_items)
    context = {
        'items': cart_items,
        'cart_count': cart_items.count(),
        'cart_subtotal': cart_subtotal,
    }
    return render(request, 'user/checkout.html', context)

@login_required
def order_confirmation(request):
    return render(request, 'order_confirmation.html')