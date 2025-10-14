from django.shortcuts import render,redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
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






#
import logging
# Set up logging
logger = logging.getLogger(__name__)
@login_required

@staff_member_required
def confirm_payment(request):
    cod_orders = Order.objects.filter(payment_method="Cash On Delivery")
    if request.method == 'POST':
        order_ids = request.POST.getlist('order_ids')
        if not order_ids:
            messages.error(request, "No orders selected for confirmation.")
            return redirect('confirm_payment')
        try:
            for order_id in order_ids:
                order = get_object_or_404(Order, id=order_id, payment_method="Cash On Delivery")
                if order.payment_status != 'Completed':
                    order.payment_status = 'Completed'
                    order.save()
                    # Send confirmation email to user
                    try:
                        user_subject = f'Order #{order.id} Payment Confirmed'
                        user_message = render_to_string('email/order_payment_confirmed.html', {'order': order})
                        user_email = EmailMessage(
                            user_subject,
                            user_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [order.email],
                        )
                        user_email.content_subtype = 'html'
                        user_email.send()
                        logger.info(f"Payment confirmation email sent to user for order #{order.id} to {order.email}")
                    except Exception as e:
                        logger.error(f"Failed to send user payment confirmation email for order #{order.id}: {str(e)}")
                        messages.warning(request, f"Payment confirmed for order #{order.id}, but failed to send user email.")
                    # Send confirmation email to admin
                    try:
                        admin_subject = f'Payment Confirmed for Order #{order.id}'
                        admin_message = render_to_string('email/order_payment_confirmed.html', {'order': order})
                        admin_email = EmailMessage(
                            admin_subject,
                            admin_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [settings.ADMIN_EMAIL],
                        )
                        admin_email.content_subtype = 'html'
                        admin_email.send()
                        logger.info(f"Payment confirmation email sent to admin for order #{order.id} to {settings.ADMIN_EMAIL}")
                    except Exception as e:
                        logger.error(f"Failed to send admin payment confirmation email for order #{order.id}: {str(e)}")
                        messages.warning(request, f"Payment confirmed for order #{order.id}, but failed to send admin email.")
            messages.success(request, f"Payments confirmed for {len(order_ids)} order(s).")
        except Exception as e:
            logger.error(f"Error confirming payments: {str(e)}")
            messages.error(request, f"Failed to confirm payments: {str(e)}")
        return redirect('confirm_payment')
    return render(request, 'admins/confirm_payment.html', {'cod_orders': cod_orders})