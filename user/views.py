

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from product.models import Cart, Product, Order
from user.forms import *
from user.filters import *
import hmac, hashlib, base64, uuid
import json
from django.views import View
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging

# Set up logging for email debugging
logger = logging.getLogger(__name__)

# Email sending function
def send_order_emails(order, request):
    # User email
    try:
        user_subject = f'Order #{order.id} Confirmation'
        user_message = render_to_string('email/order_confirmation_user.html', {'order': order})
        user_email = EmailMessage(
            user_subject,
            user_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
        )
        user_email.content_subtype = 'html'
        user_email.send()
        logger.info(f"User email sent for order #{order.id} to {order.email}")
    except Exception as e:
        logger.error(f"Failed to send user email for order #{order.id} to {order.email}: {str(e)}")
        messages.error(request, f"Failed to send user email: {str(e)}")

    # Admin email
    try:
        if not hasattr(settings, 'ADMIN_EMAIL') or not settings.ADMIN_EMAIL:
            raise ValueError("ADMIN_EMAIL is not set in settings.py")
        admin_subject = f'New Order #{order.id} Received'
        admin_message = render_to_string('email/order_confirmation_admin.html', {'order': order})
        admin_email = EmailMessage(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
        )
        admin_email.content_subtype = 'html'
        admin_email.send()
        logger.info(f"Admin email sent for order #{order.id} to {settings.ADMIN_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send admin email for order #{order.id} to {settings.ADMIN_EMAIL}: {str(e)}")
        messages.error(request, f"Failed to send admin email: {str(e)}")

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
    user = request.user.id if request.user.is_authenticated else None
    product = Product.objects.all().order_by('-id')[:4]
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user).select_related('product')
        cart_count = cart_items.count()
    else:
        cart_items = []
        cart_count = 0
    data = {
        'product': product,
        'items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, 'user/homepage.html', data)

@login_required
def productpage(request):
    product = Product.objects.all().order_by('-id')
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    cart_count = cart_items.count()
    product_filter = ProductFilter(request.GET, queryset=product)
    product_final = product_filter.qs
    data = {
        'product': product_final,
        'product_filter': product_filter,
        'items': cart_items,
        'cart_count': cart_count,
    }
    return render(request, 'user/productpage.html', data)

@login_required
def productdetail(request, product_id):
    product = Product.objects.get(id=product_id)
    data = {
        'product': product
    }
    return render(request, 'user/productdetail.html', data)

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    check_items = Cart.objects.filter(product=product, user=user)
    if check_items:
        messages.add_message(request, messages.ERROR, 'Product already in cart ! ')
        return redirect('/productpage')
    else:
        Cart.objects.create(product=product, user=user)
        messages.add_message(request, messages.SUCCESS, 'Product has been added to cart ! ')
        return redirect('/productpage')

@login_required
def cartlist(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('product')
    cart_count = cart_items.count()
    cart_subtotal = sum(item.total_price() for item in cart_items)
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
def order_confirmation(request):
    return render(request, 'order_confirmation.html')

@login_required
def orderitem(request, product_id, cart_id):
    product = Product.objects.get(id=product_id)
    cart = Cart.objects.get(id=cart_id)
    user = request.user
    form = OrderForm()
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = request.POST.get('quantity')
            price = product.product_price
            total_price = int(quantity) * float(price)
            contact_no = request.POST.get('contact_no')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            email = request.POST.get('email')

            order = Order.objects.create(
                user=user,
                product=product,
                quantity=quantity,
                address=address,
                total_price=total_price,
                payment_method=payment_method,
                contact_no=contact_no,
                email=email,
            )
            
            if order.payment_method == "Cash On Delivery":
                send_order_emails(order, request)
                cart.delete()
                messages.success(request, 'Your order has been placed successfully! Be ready with cash on delivery also kindly check your mail too . '  )
                return redirect('/cartlist')
            elif order.payment_method == "Esewa":
                return redirect(reverse('esewaform') + f'?o_id={order.id}&c_id={cart.id}')
            elif order.payment_method == "Khalti":
                send_order_emails(order, request)
                cart.delete()
                messages.success(request, 'Your order has been placed successfully! Proceed to pay with Khalti')
                return redirect('/cartlist')
            else:
                messages.error(request, 'Invalid payment option!')
        else:
            messages.error(request, 'Please provide correct credentials!')
    
    context = {
        'form': form,
        'product': product,
        'cart': cart
    }
    return render(request, 'user/orderform.html', context)

@login_required
def orderlist(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')
    context = {
        'orders': orders
    }   
    return render(request, 'user/myorder.html', context)

class EsewaView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get('o_id')
        c_id = request.GET.get('c_id')
        cart = Cart.objects.get(id=c_id)
        order = Order.objects.get(id=o_id)
        transaction_uuid = str(uuid.uuid4())
        product_code = "EPAYTEST"
        secret_key = "8gBm/:&EnhH.1/q"
        amount = order.total_price
        tax_amount = 0
        product_service_charge = 0
        product_delivery_charge = 0
        total_amount = amount + tax_amount + product_service_charge + product_delivery_charge
        data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
        signature = hmac.new(secret_key.encode('utf-8'),
                             data_to_sign.encode('utf-8'),
                             hashlib.sha256).digest()
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        
        # Updated URLs for PythonAnywhere deployment
        base_url = "https://dhirghayu.pythonanywhere.com"
        success_url = f"{base_url}/esewaverify/{order.id}/{cart.id}/"
        failure_url = f"{base_url}/esewaverify/{order.id}/{cart.id}/"
        
        data = {
            "amount": amount,
            "tax_amount": tax_amount,
            "product_service_charge": product_service_charge,
            "product_delivery_charge": product_delivery_charge,
            "total_amount": total_amount,
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "success_url": success_url,
            "failure_url": failure_url,
            "signed_field_names": "total_amount,transaction_uuid,product_code",
            "signature": signature_base64,
            "order_id": order.id,
            "cart_id": cart.id,
        }
        return render(request, "user/esewa_payment.html", {"data": data})

@login_required
def esewa_verify(request, order_id, cart_id):
    if request.method == 'GET':
        try:
            data = request.GET.get('data')
            if not data:
                logger.error(f"No data received in esewa_verify for order #{order_id}")
                messages.error(request, 'Payment verification failed: No data received')
                return redirect('/myorder')
            decoded_data = base64.b64decode(data).decode('utf-8')
            map_data = json.loads(decoded_data)
            order = Order.objects.get(id=order_id)
            cart = Cart.objects.get(id=cart_id)
            if map_data.get('status') == 'COMPLETE':
                order.payment_status = 'Completed'
                order.save()
                send_order_emails(order, request)
                cart.delete()
                messages.success(request, 'Your payment has been completed successfully! kindly check your mail too!')
                return redirect('/myorder')
            else:
                logger.error(f"Esewa payment failed for order #{order_id}: {map_data}")
                messages.error(request, 'Your payment has been FAILED!')
                return redirect('/myorder')
        except Exception as e:
            logger.error(f"Error in esewa_verify for order #{order_id}: {str(e)}")
            messages.error(request, f'Payment verification error: {str(e)}')
            return redirect('/myorder')

@login_required
def user_profile(request):
    user = request.user
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            user.email = email
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    return render(request, "user/profile.html", {"user": user})



























# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.views.decorators.http import require_POST
# from django.urls import reverse
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth import authenticate, login as auth_login, logout
# from product.models import Cart, Product, Order
# from user.forms import *
# from user.filters import *
# import hmac, hashlib, base64, uuid
# import json
# from django.views import View
# from django.core.mail import EmailMessage
# from django.template.loader import render_to_string
# from django.conf import settings
# import logging

# # Set up logging for email debugging
# logger = logging.getLogger(__name__)

# # Email sending function
# def send_order_emails(order, request):
#     # User email
#     try:
#         user_subject = f'Order #{order.id} Confirmation'
#         user_message = render_to_string('email/order_confirmation_user.html', {'order': order})
#         user_email = EmailMessage(
#             user_subject,
#             user_message,
#             settings.DEFAULT_FROM_EMAIL,
#             [order.email],
#         )
#         user_email.content_subtype = 'html'
#         user_email.send()
#         logger.info(f"User email sent for order #{order.id} to {order.email}")
#     except Exception as e:
#         logger.error(f"Failed to send user email for order #{order.id} to {order.email}: {str(e)}")
#         messages.error(request, f"Failed to send user email: {str(e)}")

#     # Admin email
#     try:
#         if not hasattr(settings, 'ADMIN_EMAIL') or not settings.ADMIN_EMAIL:
#             raise ValueError("ADMIN_EMAIL is not set in settings.py")
#         admin_subject = f'New Order #{order.id} Received'
#         admin_message = render_to_string('email/order_confirmation_admin.html', {'order': order})
#         admin_email = EmailMessage(
#             admin_subject,
#             admin_message,
#             settings.DEFAULT_FROM_EMAIL,
#             [settings.ADMIN_EMAIL],
#         )
#         admin_email.content_subtype = 'html'
#         admin_email.send()
#         logger.info(f"Admin email sent for order #{order.id} to {settings.ADMIN_EMAIL}")
#     except Exception as e:
#         logger.error(f"Failed to send admin email for order #{order.id} to {settings.ADMIN_EMAIL}: {str(e)}")
#         messages.error(request, f"Failed to send admin email: {str(e)}")

# def register(request):
#     if request.method=="POST":
#         form=UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.add_message(request, messages.SUCCESS,'User account has been created Sucessfully ! .')
#             return redirect('/register')
#         else:
#              messages.add_message(request, messages.ERROR,' Please provide correct credentials !.')
#              return render(request,'user/register.html',{'form':form})

#     context={
#         'form':UserCreationForm
#     }
#     return render(request,'user/register.html',context)

# def login(request):
#     if request.method=="POST":
#         form=LoginForm(request.POST)
#         if form.is_valid():
#             data=form.cleaned_data
#         user=authenticate(request,username=data['username'],password=data['password'])
#         if user is not None:
#             auth_login(request,user)
#             if user.is_staff:
#                 return redirect('admins')
#             else:
#                 return redirect('/')
#         else:
#             messages.add_message(request, messages.ERROR,' OOPs, either username or password is INVALID !.')
#             return render(request,'user/loginform.html',{'form':form})
        
#     context={
#         'form':LoginForm
#     }
#     return render(request,'user/loginform.html',context)
    
# def logoutuser(request):
#     logout(request)
#     return redirect('/login')

# def homepage(request):
#     user = request.user.id if request.user.is_authenticated else None
#     product = Product.objects.all().order_by('-id')[:4]
#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user).select_related('product')
#         cart_count = cart_items.count()
#     else:
#         cart_items = []
#         cart_count = 0
#     data = {
#         'product': product,
#         'items': cart_items,
#         'cart_count': cart_count,
#     }
#     return render(request, 'user/homepage.html', data)

# @login_required
# def productpage(request):
#     product = Product.objects.all().order_by('-id')
#     cart_items = Cart.objects.filter(user=request.user).select_related('product')
#     cart_count = cart_items.count()
#     product_filter = ProductFilter(request.GET, queryset=product)
#     product_final = product_filter.qs
#     data = {
#         'product': product_final,
#         'product_filter': product_filter,
#         'items': cart_items,
#         'cart_count': cart_count,
#     }
#     return render(request, 'user/productpage.html', data)

# @login_required
# def productdetail(request, product_id):
#     product = Product.objects.get(id=product_id)
#     data = {
#         'product': product
#     }
#     return render(request, 'user/productdetail.html', data)

# @login_required
# def add_to_cart(request, product_id):
#     product = Product.objects.get(id=product_id)
#     user = request.user
#     check_items = Cart.objects.filter(product=product, user=user)
#     if check_items:
#         messages.add_message(request, messages.ERROR, 'Product already in cart ! ')
#         return redirect('/productpage')
#     else:
#         Cart.objects.create(product=product, user=user)
#         messages.add_message(request, messages.SUCCESS, 'Product has been added to cart ! ')
#         return redirect('/productpage')

# @login_required
# def cartlist(request):
#     cart_items = Cart.objects.filter(user=request.user).select_related('product')
#     cart_count = cart_items.count()
#     cart_subtotal = sum(item.total_price() for item in cart_items)
#     context = {
#         'items': cart_items,
#         'cart_count': cart_count,
#         'cart_subtotal': cart_subtotal,
#     }
#     return render(request, 'user/cart.html', context)

# @login_required
# def get_cart_count(request):
#     cart_count = Cart.objects.filter(user=request.user).count()
#     return JsonResponse({'cart_count': cart_count})

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
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=400)

# @login_required
# def remove_from_cart(request, product_id):
#     cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
#     cart_item.delete()
#     messages.success(request, f"{cart_item.product.product_name} removed from cart.")
#     return redirect('cartlist')

# @login_required
# def clear_cart(request):
#     Cart.objects.filter(user=request.user).delete()
#     messages.success(request, "Your cart has been cleared.")
#     return redirect('cartlist')

# @login_required
# def order_confirmation(request):
#     return render(request, 'order_confirmation.html')

# @login_required
# def orderitem(request, product_id, cart_id):
#     product = Product.objects.get(id=product_id)
#     cart = Cart.objects.get(id=cart_id)
#     user = request.user
#     form = OrderForm()
    
#     if request.method == "POST":
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             quantity = request.POST.get('quantity')
#             price = product.product_price
#             total_price = int(quantity) * float(price)
#             contact_no = request.POST.get('contact_no')
#             address = request.POST.get('address')
#             payment_method = request.POST.get('payment_method')
#             email = request.POST.get('email')

#             order = Order.objects.create(
#                 user=user,
#                 product=product,
#                 quantity=quantity,
#                 address=address,
#                 total_price=total_price,
#                 payment_method=payment_method,
#                 contact_no=contact_no,
#                 email=email,
#             )
            
#             if order.payment_method == "Cash On Delivery":
#                 send_order_emails(order, request)
#                 cart.delete()
#                 messages.success(request, 'Your order has been placed successfully! Be ready with cash on delivery also kindly check your mail too . '  )
#                 return redirect('/cartlist')
#             elif order.payment_method == "Esewa":
#                 return redirect(reverse('esewaform') + f'?o_id={order.id}&c_id={cart.id}')
#             elif order.payment_method == "Khalti":
#                 send_order_emails(order, request)
#                 cart.delete()
#                 messages.success(request, 'Your order has been placed successfully! Proceed to pay with Khalti')
#                 return redirect('/cartlist')
#             else:
#                 messages.error(request, 'Invalid payment option!')
#         else:
#             messages.error(request, 'Please provide correct credentials!')
    
#     context = {
#         'form': form,
#         'product': product,
#         'cart': cart
#     }
#     return render(request, 'user/orderform.html', context)

# @login_required
# def orderlist(request):
#     user = request.user
#     orders = Order.objects.filter(user=user).order_by('-id')
#     context = {
#         'orders': orders
#     }   
#     return render(request, 'user/myorder.html', context)

# class EsewaView(View):
#     def get(self, request, *args, **kwargs):
#         o_id = request.GET.get('o_id')
#         c_id = request.GET.get('c_id')
#         cart = Cart.objects.get(id=c_id)
#         order = Order.objects.get(id=o_id)
#         transaction_uuid = str(uuid.uuid4())
#         product_code = "EPAYTEST"
#         secret_key = "8gBm/:&EnhH.1/q"
#         amount = order.total_price
#         tax_amount = 0
#         product_service_charge = 0
#         product_delivery_charge = 0
#         total_amount = amount + tax_amount + product_service_charge + product_delivery_charge
#         data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
#         signature = hmac.new(secret_key.encode('utf-8'),
#                              data_to_sign.encode('utf-8'),
#                              hashlib.sha256).digest()
#         signature_base64 = base64.b64encode(signature).decode('utf-8')
#         data = {
#             "amount": amount,
#             "tax_amount": tax_amount,
#             "product_service_charge": product_service_charge,
#             "product_delivery_charge": product_delivery_charge,
#             "total_amount": total_amount,
#             "transaction_uuid": transaction_uuid,
#             "product_code": product_code,
#             "success_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
#             "failure_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
#             "signed_field_names": "total_amount,transaction_uuid,product_code",
#             "signature": signature_base64,
#             "order_id": order.id,
#             "cart_id": cart.id,
#         }
#         return render(request, "user/esewa_payment.html", {"data": data})

# @login_required
# def esewa_verify(request, order_id, cart_id):
#     if request.method == 'GET':
#         try:
#             data = request.GET.get('data')
#             if not data:
#                 logger.error(f"No data received in esewa_verify for order #{order_id}")
#                 messages.error(request, 'Payment verification failed: No data received')
#                 return redirect('/myorder')
#             decoded_data = base64.b64decode(data).decode('utf-8')
#             map_data = json.loads(decoded_data)
#             order = Order.objects.get(id=order_id)
#             cart = Cart.objects.get(id=cart_id)
#             if map_data.get('status') == 'COMPLETE':
#                 order.payment_status = 'Completed'
#                 order.save()
#                 send_order_emails(order, request)
#                 cart.delete()
#                 messages.success(request, 'Your payment has been completed successfully! kindly check your mail too!')
#                 return redirect('/myorder')
#             else:
#                 logger.error(f"Esewa payment failed for order #{order_id}: {map_data}")
#                 messages.error(request, 'Your payment has been FAILED!')
#                 return redirect('/myorder')
#         except Exception as e:
#             logger.error(f"Error in esewa_verify for order #{order_id}: {str(e)}")
#             messages.error(request, f'Payment verification error: {str(e)}')
#             return redirect('/myorder')

# @login_required
# def user_profile(request):
#     user = request.user
#     if request.method == "POST":
#         email = request.POST.get("email")
#         if email:
#             user.email = email
#             user.save()
#             messages.success(request, "Profile updated successfully!")
#             return redirect("profile")
#     return render(request, "user/profile.html", {"user": user})



















# # from django.shortcuts import render, redirect, get_object_or_404
# # from django.http import JsonResponse
# # from django.contrib.auth.decorators import login_required
# # from django.contrib import messages
# # from django.views.decorators.http import require_POST
# # from django.urls import reverse
# # from django.contrib.auth.models import User
# # from django.contrib.auth.forms import UserCreationForm
# # from django.contrib.auth import authenticate, login as auth_login, logout
# # from product.models import Cart, Product, Order
# # from user.forms import *
# # from user.filters import *
# # import hmac, hashlib, base64, uuid
# # import json
# # from django.views import View
# # from django.core.mail import EmailMessage
# # from django.template.loader import render_to_string
# # from django.conf import settings
# # import logging

# # # Set up logging for email debugging
# # logger = logging.getLogger(__name__)

# # # Email sending function
# # def send_order_emails(order, request):
# #     try:
# #         # User email
# #         user_subject = f'Order #{order.id} Confirmation'
# #         user_message = render_to_string('email/order_confirmation_user.html', {'order': order})
# #         user_email = EmailMessage(
# #             user_subject,
# #             user_message,
# #             settings.DEFAULT_FROM_EMAIL,
# #             [order.email],
# #         )
# #         user_email.content_subtype = 'html'
# #         user_email.send()
# #         logger.info(f"User email sent for order #{order.id} to {order.email}")

# #         # Admin email
# #         admin_subject = f'New Order #{order.id} Received'
# #         admin_message = render_to_string('email/order_confirmation_admin.html', {'order': order})
# #         admin_email = EmailMessage(
# #             admin_subject,
# #             admin_message,
# #             settings.DEFAULT_FROM_EMAIL,
# #             [settings.ADMIN_EMAIL],
# #         )
# #         admin_email.content_subtype = 'html'
# #         admin_email.send()
# #         logger.info(f"Admin email sent for order #{order.id} to {settings.ADMIN_EMAIL}")
# #     except Exception as e:
# #         logger.error(f"Failed to send emails for order #{order.id}: {str(e)}")
# #         messages.error(request, f"Failed to send email notifications: {str(e)}")

# # def register(request):
# #     if request.method=="POST":
# #         form=UserCreationForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             messages.add_message(request, messages.SUCCESS,'User account has been created Sucessfully ! .')
# #             return redirect('/register')
# #         else:
# #              messages.add_message(request, messages.ERROR,' Please provide correct credentials !.')
# #              return render(request,'user/register.html',{'form':form})

# #     context={
# #         'form':UserCreationForm
# #     }
# #     return render(request,'user/register.html',context)

# # def login(request):
# #     if request.method=="POST":
# #         form=LoginForm(request.POST)
# #         if form.is_valid():
# #             data=form.cleaned_data
# #         user=authenticate(request,username=data['username'],password=data['password'])
# #         if user is not None:
# #             auth_login(request,user)
# #             if user.is_staff:
# #                 return redirect('admins')
# #             else:
# #                 return redirect('/')
# #         else:
# #             messages.add_message(request, messages.ERROR,' OOPs, either username or password is INVALID !.')
# #             return render(request,'user/loginform.html',{'form':form})
        
# #     context={
# #         'form':LoginForm
# #     }
# #     return render(request,'user/loginform.html',context)
    
# # def logoutuser(request):
# #     logout(request)
# #     return redirect('/login')

# # def homepage(request):
# #     user = request.user.id if request.user.is_authenticated else None
# #     product = Product.objects.all().order_by('-id')[:4]
# #     if request.user.is_authenticated:
# #         cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #         cart_count = cart_items.count()
# #     else:
# #         cart_items = []
# #         cart_count = 0
# #     data = {
# #         'product': product,
# #         'items': cart_items,
# #         'cart_count': cart_count,
# #     }
# #     return render(request, 'user/homepage.html', data)

# # @login_required
# # def productpage(request):
# #     product = Product.objects.all().order_by('-id')
# #     cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #     cart_count = cart_items.count()
# #     product_filter = ProductFilter(request.GET, queryset=product)
# #     product_final = product_filter.qs
# #     data = {
# #         'product': product_final,
# #         'product_filter': product_filter,
# #         'items': cart_items,
# #         'cart_count': cart_count,
# #     }
# #     return render(request, 'user/productpage.html', data)

# # @login_required
# # def productdetail(request, product_id):
# #     product = Product.objects.get(id=product_id)
# #     data = {
# #         'product': product
# #     }
# #     return render(request, 'user/productdetail.html', data)

# # @login_required
# # def add_to_cart(request, product_id):
# #     product = Product.objects.get(id=product_id)
# #     user = request.user
# #     check_items = Cart.objects.filter(product=product, user=user)
# #     if check_items:
# #         messages.add_message(request, messages.ERROR, 'Product already in cart ! ')
# #         return redirect('/productpage')
# #     else:
# #         Cart.objects.create(product=product, user=user)
# #         messages.add_message(request, messages.SUCCESS, 'Product has been added to cart ! ')
# #         return redirect('/productpage')

# # @login_required
# # def cartlist(request):
# #     cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #     cart_count = cart_items.count()
# #     cart_subtotal = sum(item.total_price() for item in cart_items)
# #     context = {
# #         'items': cart_items,
# #         'cart_count': cart_count,
# #         'cart_subtotal': cart_subtotal,
# #     }
# #     return render(request, 'user/cart.html', context)

# # @login_required
# # def get_cart_count(request):
# #     cart_count = Cart.objects.filter(user=request.user).count()
# #     return JsonResponse({'cart_count': cart_count})

# # @require_POST
# # @login_required
# # def update_quantity(request, product_id):
# #     try:
# #         cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
# #         action = request.POST.get('action')
# #         if action == 'increase':
# #             cart_item.quantity += 1
# #         elif action == 'decrease' and cart_item.quantity > 1:
# #             cart_item.quantity -= 1
# #         cart_item.save()
# #         return JsonResponse({
# #             'success': True,
# #             'quantity': cart_item.quantity,
# #             'total_price': cart_item.quantity * cart_item.product.product_price,
# #             'cart_subtotal': sum(item.quantity * item.product.product_price for item in Cart.objects.filter(user=request.user))
# #         })
# #     except Exception as e:
# #         return JsonResponse({'success': False, 'error': str(e)}, status=400)

# # @login_required
# # def remove_from_cart(request, product_id):
# #     cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
# #     cart_item.delete()
# #     messages.success(request, f"{cart_item.product.product_name} removed from cart.")
# #     return redirect('cartlist')

# # @login_required
# # def clear_cart(request):
# #     Cart.objects.filter(user=request.user).delete()
# #     messages.success(request, "Your cart has been cleared.")
# #     return redirect('cartlist')

# # @login_required
# # def order_confirmation(request):
# #     return render(request, 'order_confirmation.html')

# # @login_required
# # def orderitem(request, product_id, cart_id):
# #     product = Product.objects.get(id=product_id)
# #     cart = Cart.objects.get(id=cart_id)
# #     user = request.user
# #     form = OrderForm()
    
# #     if request.method == "POST":
# #         form = OrderForm(request.POST)
# #         if form.is_valid():
# #             quantity = request.POST.get('quantity')
# #             price = product.product_price
# #             total_price = int(quantity) * float(price)
# #             contact_no = request.POST.get('contact_no')
# #             address = request.POST.get('address')
# #             payment_method = request.POST.get('payment_method')
# #             email = request.POST.get('email')

# #             order = Order.objects.create(
# #                 user=user,
# #                 product=product,
# #                 quantity=quantity,
# #                 address=address,
# #                 total_price=total_price,
# #                 payment_method=payment_method,
# #                 contact_no=contact_no,
# #                 email=email,
# #             )
            
# #             if order.payment_method == "Cash On Delivery":
# #                 send_order_emails(order, request)
# #                 cart.delete()
# #                 messages.success(request, 'Your order has been placed successfully! Be ready with cash on delivery. Check your mail too . '  )
# #                 return redirect('/cartlist')
# #             elif order.payment_method == "Esewa":
# #                 return redirect(reverse('esewaform') + f'?o_id={order.id}&c_id={cart.id}')
# #             elif order.payment_method == "Khalti":
# #                 send_order_emails(order, request)  # Placeholder for Khalti
# #                 cart.delete()
# #                 messages.success(request, 'Your order has been placed successfully! Proceed to pay with Khalti')
# #                 return redirect('/cartlist')
# #             else:
# #                 messages.error(request, 'Invalid payment option!')
# #         else:
# #             messages.error(request, 'Please provide correct credentials!')
    
# #     context = {
# #         'form': form,
# #         'product': product,
# #         'cart': cart
# #     }
# #     return render(request, 'user/orderform.html', context)

# # @login_required
# # def orderlist(request):
# #     user = request.user
# #     orders = Order.objects.filter(user=user).order_by('-id')
# #     context = {
# #         'orders': orders
# #     }   
# #     return render(request, 'user/myorder.html', context)

# # class EsewaView(View):
# #     def get(self, request, *args, **kwargs):
# #         o_id = request.GET.get('o_id')
# #         c_id = request.GET.get('c_id')
# #         cart = Cart.objects.get(id=c_id)
# #         order = Order.objects.get(id=o_id)
# #         transaction_uuid = str(uuid.uuid4())
# #         product_code = "EPAYTEST"
# #         secret_key = "8gBm/:&EnhH.1/q"
# #         amount = order.total_price
# #         tax_amount = 0
# #         product_service_charge = 0
# #         product_delivery_charge = 0
# #         total_amount = amount + tax_amount + product_service_charge + product_delivery_charge
# #         data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
# #         signature = hmac.new(secret_key.encode('utf-8'),
# #                              data_to_sign.encode('utf-8'),
# #                              hashlib.sha256).digest()
# #         signature_base64 = base64.b64encode(signature).decode('utf-8')
# #         data = {
# #             "amount": amount,
# #             "tax_amount": tax_amount,
# #             "product_service_charge": product_service_charge,
# #             "product_delivery_charge": product_delivery_charge,
# #             "total_amount": total_amount,
# #             "transaction_uuid": transaction_uuid,
# #             "product_code": product_code,
# #             "success_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
# #             "failure_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
# #             "signed_field_names": "total_amount,transaction_uuid,product_code",
# #             "signature": signature_base64,
# #             "order_id": order.id,
# #             "cart_id": cart.id,
# #         }
# #         return render(request, "user/esewa_payment.html", {"data": data})

# # @login_required
# # def esewa_verify(request, order_id, cart_id):
# #     if request.method == 'GET':
# #         try:
# #             data = request.GET.get('data')
# #             if not data:
# #                 logger.error(f"No data received in esewa_verify for order #{order_id}")
# #                 messages.error(request, 'Payment verification failed: No data received')
# #                 return redirect('/myorder')
# #             decoded_data = base64.b64decode(data).decode('utf-8')
# #             map_data = json.loads(decoded_data)
# #             order = Order.objects.get(id=order_id)
# #             cart = Cart.objects.get(id=cart_id)
# #             if map_data.get('status') == 'COMPLETE':
# #                 order.payment_status = 'Completed'
# #                 order.save()
# #                 send_order_emails(order, request)
# #                 cart.delete()
# #                 messages.success(request, 'Your payment has been completed successfully!')
# #                 return redirect('/myorder')
# #             else:
# #                 logger.error(f"Esewa payment failed for order #{order_id}: {map_data}")
# #                 messages.error(request, 'Your payment has been FAILED!')
# #                 return redirect('/myorder')
# #         except Exception as e:
# #             logger.error(f"Error in esewa_verify for order #{order_id}: {str(e)}")
# #             messages.error(request, f'Payment verification error: {str(e)}')
# #             return redirect('/myorder')

# # @login_required
# # def user_profile(request):
# #     user = request.user
# #     if request.method == "POST":
# #         email = request.POST.get("email")
# #         if email:
# #             user.email = email
# #             user.save()
# #             messages.success(request, "Profile updated successfully!")
# #             return redirect("profile")
# #     return render(request, "user/profile.html", {"user": user})



# ######################################






















# # from django.shortcuts import render,redirect
# # from product.models import Cart, Product, Order
# # from django.contrib.auth.models import User
# # from django.contrib.auth.forms import UserCreationForm
# # from django.contrib import messages
# # from .filters import *
# # from django.contrib.auth import authenticate, login as auth_login, logout 
# # from user.forms import *
# # from django.contrib.auth.decorators import login_required
# # from django.urls import reverse
# # from django.views import View
# # from django.core.mail import EmailMessage


# # ##
# # #email
# # from django.core.mail import EmailMessage
# # from django.template.loader import render_to_string
# # from django.conf import settings
# # ##
# # # from adminpage.views import adminhome
# # # Create your views here.


# # def register(request):
# #     if request.method=="POST":
# #         form=UserCreationForm(request.POST)
# #         if form.is_valid():
# #             form.save()
# #             messages.add_message(request, messages.SUCCESS,'User account has been created Sucessfully ! .')
# #             return redirect('/register')
# #         else:
# #              messages.add_message(request, messages.ERROR,' Please provide correct credentials !.')
# #              return render(request,'user/register.html',{'form':form})

# #     context={
# #         'form':UserCreationForm
# #     }
# #     return render(request,'user/register.html',context)



# # def login(request):
# #     if request.method=="POST":
# #         form=LoginForm(request.POST)
# #         if form.is_valid():
# #             data=form.cleaned_data
# #         user=authenticate(request,username=data['username'],password=data['password'])
# #         if user is not None:
# #             auth_login(request,user)
# #             if user.is_staff:
# #                 return redirect('admins')
# #             else:
# #                 return redirect('/')
# #         else:
# #             messages.add_message(request, messages.ERROR,' OOPs, either username or password is INVALID !.')
# #             return render(request,'user/loginform.html',{'form':form})
        
# #     context={
# #         'form':LoginForm
# #     }
# #     return render(request,'user/loginform.html',context)
    
    

# # def logoutuser(request):
# #     logout(request)
# #     return redirect('/login')



# # def homepage(request):
# #     # user=request.user.id
# #     user= request.user.id if request.user.is_authenticated else None
# #     product=Product.objects.all().order_by('-id')[:4]

# #     # cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #     # cart_count = cart_items.count()
# #      # Only get cart items if user is authenticated
# #     if request.user.is_authenticated:
# #         cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #         cart_count = cart_items.count()
# #     else:
# #         cart_items = []
# #         cart_count = 0


# #     data={
# #         'product':product,
# #          'items': cart_items,
# #         'cart_count': cart_count,
# #     }

# #     return render(request,'user/homepage.html',data)


# # @login_required
# # def productpage(request):
# #     product=Product.objects.all().order_by('-id')
# #     cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #     cart_count = cart_items.count()
# #     product_filter=ProductFilter(request.GET,queryset=product)
# #     product_final=product_filter.qs
# #     data={
# #         'product':product_final,
# #         'product_filter':product_filter,
# #          'items': cart_items,
# #         'cart_count': cart_count,
# #     }

# #     return render(request,'user/productpage.html',data)

# # @login_required
# # def productdetail(request,product_id):
# #     product=Product.objects.get(id=product_id)
# #     data={
# #         'product':product
# #     }

# #     return render(request,'user/productdetail.html',data)

# # @login_required
# # def add_to_cart(request,product_id):
# #     product=Product.objects.get(id=product_id)
# #     user=request.user
# #     check_items=Cart.objects.filter(product=product,user=user)
# #     if check_items:
# #         messages.add_message(request,messages.ERROR,'Product already in cart ! ')
# #         return redirect('/productpage')
# #     else:
# #         Cart.objects.create(product=product,user=user)
# #         messages.add_message(request,messages.SUCCESS,'Product has been added to cart ! ')
# #         return redirect('/productpage')
    





# # # 
# # # 
# # # 
# # # ecommerce/views.py
# # from django.shortcuts import render, redirect, get_object_or_404
# # from django.http import JsonResponse
# # from django.contrib.auth.decorators import login_required
# # from django.contrib import messages

# # from django.views.decorators.http import require_POST
# # from django.urls import reverse
# # from django.db.models import Sum





# # ###
# # # New views for cart.html
# # @login_required
# # def cartlist(request):
# #     cart_items = Cart.objects.filter(user=request.user).select_related('product')
# #     cart_count = cart_items.count()
    
# #     # Calculate subtotal using the total_price method from your model
# #     cart_subtotal = sum(item.total_price() for item in cart_items)

# #     context = {
# #         'items': cart_items,
# #         'cart_count': cart_count,
# #         'cart_subtotal': cart_subtotal,
# #     }
# #     return render(request, 'user/cart.html', context)


# # @login_required
# # def get_cart_count(request):
# #     cart_count = Cart.objects.filter(user=request.user).count()
# #     return JsonResponse({'cart_count': cart_count})

# # @require_POST
# # @login_required
# # def update_quantity(request, product_id):
# #     try:
# #         cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
# #         action = request.POST.get('action')
# #         if action == 'increase':
# #             cart_item.quantity += 1
# #         elif action == 'decrease' and cart_item.quantity > 1:
# #             cart_item.quantity -= 1
# #         cart_item.save()
# #         return JsonResponse({
# #             'success': True,
# #             'quantity': cart_item.quantity,
# #             'total_price': cart_item.quantity * cart_item.product.product_price,
# #             'cart_subtotal': sum(item.quantity * item.product.product_price for item in Cart.objects.filter(user=request.user))
# #         })
# #     except Exception as e:
# #         return JsonResponse({'success': False, 'error': str(e)}, status=400)

# # @login_required
# # def remove_from_cart(request, product_id):
# #     cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
# #     cart_item.delete()
# #     messages.success(request, f"{cart_item.product.product_name} removed from cart.")
# #     return redirect('cartlist')

# # @login_required
# # def clear_cart(request):
# #     Cart.objects.filter(user=request.user).delete()
# #     messages.success(request, "Your cart has been cleared.")
# #     return redirect('cartlist')


# # @login_required
# # def order_confirmation(request):
# #     return render(request, 'order_confirmation.html')








# # #
# # @login_required
# # def orderitem(request, product_id, cart_id):
# #     product = Product.objects.get(id=product_id)
# #     cart = Cart.objects.get(id=cart_id)
# #     user = request.user
    
# #     # Initialize form for GET requests
# #     form = OrderForm()
    
# #     if request.method == "POST":
# #         form = OrderForm(request.POST)
# #         if form.is_valid():
# #             quantity = request.POST.get('quantity')
# #             price = product.product_price
# #             total_price = int(quantity) * float(price)
# #             contact_no = request.POST.get('contact_no')
# #             address = request.POST.get('address')
# #             payment_method = request.POST.get('payment_method')
# #             email = request.POST.get('email')

# #             order = Order.objects.create(
# #                 user=user,
# #                 product=product,
# #                 quantity=quantity,
# #                 address=address,
# #                 total_price=total_price,
# #                 payment_method=payment_method,
# #                 contact_no=contact_no,
# #                 email=email,
# #                 # payment_status='Pending'
# #             )
            
# #             if order.payment_method == "Cash On Delivery":
# #                 send_order_emails(order)  # Send emails for COD
# #                 cart.delete()
# #                 messages.success(request, 'Your order has been placed successfully! Be ready with cash on delivery')
# #                 return redirect('/cartlist')
# #             elif order.payment_method == "Esewa":
# #                 # 
# #                 return redirect(reverse('esewaform') + f'?o_id={order.id}&c_id={cart.id}')
# #                 # return redirect(reverse('esewaform/') + '?o_id=' + str(order.id) + '&c_id=' + str(cart.id))
# #                 # cart.delete()
# #                 # messages.success(request, 'Your order has been placed successfully! Proceed to pay with Esewa')
# #                 return redirect('/cartlist')
           
# #             else:
# #                 messages.error(request, 'Invalid payment option!')
# #         else:
# #             messages.error(request, 'Please provide correct credentials!')
    
# #     # Context for both GET and POST requests
# #     context = {
# #         'form': form,
# #         'product': product,
# #         'cart': cart
# #     }
# #     return render(request, 'user/orderform.html', context)



# # @login_required
# # def orderlist(request):
# #     user=request.user
# #     orders=Order.objects.filter(user=user).order_by('-id')
# #     context={
# #         'orders':orders
# #     }   
# #     return render(request,'user/myorder.html',context)








# # ###
# # import hmac, hashlib, base64, uuid
# # from django.views import View
# # from django.shortcuts import render
# # from product.models import Cart, Order

# # class EsewaView(View):
# #     def get(self, request, *args, **kwargs):
# #         o_id = request.GET.get('o_id')
# #         c_id = request.GET.get('c_id')

# #         cart = Cart.objects.get(id=c_id)
# #         order = Order.objects.get(id=o_id)

# #         transaction_uuid = str(uuid.uuid4())
# #         product_code = "EPAYTEST"
# #         secret_key = "8gBm/:&EnhH.1/q"

# #         # === Correct total ===
# #         amount = order.total_price
# #         tax_amount = 0
# #         product_service_charge = 0
# #         product_delivery_charge = 0
# #         total_amount = amount + tax_amount + product_service_charge + product_delivery_charge

# #         # === Signature ===
# #         data_to_sign = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
# #         signature = hmac.new(secret_key.encode('utf-8'),
# #                              data_to_sign.encode('utf-8'),
# #                              hashlib.sha256).digest()
# #         signature_base64 = base64.b64encode(signature).decode('utf-8')

# #         data = {
# #             "amount": amount,
# #             "tax_amount": tax_amount,
# #             "product_service_charge": product_service_charge,
# #             "product_delivery_charge": product_delivery_charge,
# #             "total_amount": total_amount,
# #             "transaction_uuid": transaction_uuid,
# #             "product_code": product_code,
# #            "success_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
# #             "failure_url": f"http://localhost:8000/esewaverify/{order.id}/{cart.id}/",
# #             "signed_field_names": "total_amount,transaction_uuid,product_code",
# #             "signature": signature_base64,
# #             "order_id": order.id,
# #             "cart_id": cart.id,
# #         }

# #         return render(request, "user/esewa_payment.html", {"data": data})



# # import json
# # @login_required
# # def esewa_verify(request,order_id,cart_id):
# #     if request.method=='GET':
# #         data=request.GET.get('data')
# #         decoded_data=base64.b64decode(data).decode('utf-8')
# #         map_data=json.loads(decoded_data)
# #         order=Order.objects.get(id=order_id)
# #         cart=Cart.objects.get(id=cart_id)
# #         if map_data.get('status')=='COMPLETE':
# #             order.payment_status='Completed'
# #             order.save()
# #             send_order_emails(order)  # Send emails after successful payment
# #             cart.delete()
# #             messages.add_message(request,messages.SUCCESS,'Your payment has been completed successfully ! ')
# #             return redirect('/myorder')
# #         else:
# #             # order.payment_status=False
# #             # order.save()
# #             messages.add_message(request,messages.ERROR,'Your payment has been FAILED ! ')
# #             return redirect('/myorder')
  

# # from django.contrib.auth.decorators import login_required
# # from django.shortcuts import render, redirect
# # from django.contrib import messages

# # @login_required
# # def user_profile(request):
# #     user = request.user

# #     if request.method == "POST":
# #         email = request.POST.get("email")
# #         if email:
# #             user.email = email
# #             user.save()
# #             messages.success(request, "Profile updated successfully!")
# #             return redirect("profile")

# #     return render(request, "user/profile.html", {"user": user})




# # # # email|
# # # def send_order_emails(order):
# # #     # User email
# # #     user_subject = f'Order #{order.id} Confirmation'
# # #     user_message = render_to_string('email/order_confirmation_user.html', {'order': order})
# # #     user_email = EmailMessage(
# # #         user_subject,
# # #         user_message,
# # #         settings.DEFAULT_FROM_EMAIL,
# # #         [order.email],
# # #     )
# # #     user_email.content_subtype = 'html'  # Enable HTML content
# # #     user_email.send()

# # #     # Admin email
# # #     admin_subject = f'New Order #{order.id} Received'
# # #     admin_message = render_to_string('email/order_confirmation_admin.html', {'order': order})
# # #     admin_email = EmailMessage(
# # #         admin_subject,
# # #         admin_message,
# # #         settings.DEFAULT_FROM_EMAIL,
# # #         [settings.ADMIN_EMAIL],
# # #     )
# # #     admin_email.content_subtype = 'html'
# # #     admin_email.send()



# # # Email sending function
# # def send_order_emails(order):
# #     try:
# #         # User email
# #         user_subject = f'Order #{order.id} Confirmation'
# #         user_message = render_to_string('email/order_confirmation_user.html', {'order': order})
# #         user_email = EmailMessage(
# #             user_subject,
# #             user_message,
# #             settings.DEFAULT_FROM_EMAIL,
# #             [order.email],
# #         )
# #         user_email.content_subtype = 'html'
# #         user_email.send()

# #         # Admin email
# #         admin_subject = f'New Order #{order.id} Received'
# #         admin_message = render_to_string('email/order_confirmation_admin.html', {'order': order})
# #         admin_email = EmailMessage(
# #             admin_subject,
# #             admin_message,
# #             settings.DEFAULT_FROM_EMAIL,
# #             [settings.ADMIN_EMAIL],
# #         )
# #         admin_email.content_subtype = 'html'
# #         admin_email.send()
# #     except Exception as e:
# #         messages.error(request, f'Failed to send email notifications: {str(e)}')