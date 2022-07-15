from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
from django.conf import settings
from store.models import Product

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

import razorpay
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json



# Create your views here.
def payments(request):
    return HttpResponse('done')

def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    if request.method == "POST":
        form = OrderForm(request.POST)
        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total += (cart_item.product.price*cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = int(grand_total)
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR') 
            data.save()

            #Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date+str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            
            client = razorpay.Client(auth = (settings.KEY, settings.SECRET))
            payment = client.order.create({'amount': int(grand_total*100), 'currency' : "INR", 'payment_capture' : 1})
            order.razor_pay_order_id = payment['id']
            order.status = payment['status']
            order.save()

            print("*****************",payment,"*******************")
            
            context = {
                'order': order,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : int(grand_total*100),
                'payment' : payment
            }
            
            return render(request, 'orders/payments.html', context)
    
    else:
        return redirect('checkout')

def success(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(user = request.user, is_ordered=False, razor_pay_order_id = order_id)

    payment = Payment(
        user = request.user,
        payment_id = order_id,
        payment_method = "RazorPay",
        amount_paid = order.order_total,
        status = order.status,
    )
    payment.save()

    print("order:",order.status)
    order.payment = payment
    order.is_ordered = True
    order.save()

    #Move the Cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)
    print('cart_items:',cart_items)

    for item in cart_items:
        print('item:',item)
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()

        print('orderproduct: ',orderproduct)

        #Redcue the quality of the sold products

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    #Clear Cart
    CartItem.objects.filter(user=request.user).delete()

    #Send Order Received email to customer:
    mail_subject = 'Thank You for your order!'
    message = render_to_string('orders/reset_password_email.html',{
        'user'  : request.user,
        'order' : order,
                
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    ordered_products = OrderProduct.objects.filter(order_id=order.id)

    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price*i.quantity
       

    context = {
            'order' : order,
            'ordered_products' :  ordered_products,
            'order_number' : order.order_number,
            'payment_id' : payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
        }



    return render(request, 'orders/order_complete.html', context)

'''def order_complete(request):
    return render(request, 'orders/order_complete.html', context)'''

