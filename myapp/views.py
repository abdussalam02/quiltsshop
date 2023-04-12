from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from .models import *
from .forms import *
import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def index(request):
    data = ProductVariant.objects.all()[:8]
    info = Information.objects.get(id=1)
    carousal = Carousal.objects.all().reverse()[:3]
    offer = Offer.objects.all().reverse()
    offer1 = offer[:2]
    offer2 = offer[2:4]
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, "index.html", {"variants": data, "recent_variants": data[::-1], "cart_count": cart_count, "wish_count": wish_count, "information": info, "carousal": carousal, "offer1": offer1, "offer2": offer2})

def all_product(request):
    data = ProductVariant.objects.all()
    paginator = Paginator(data, 4) # Show 10 items per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'shop.html', {"variants": variants, "cart_count": cart_count, "wish_count": wish_count, "category": False, "information": info})

def product(request, slug):
    variant = ProductVariant.objects.filter(slug=slug).first()
    reviews = Review.objects.filter(product=variant.product).all()
    product = Product.objects.get(id=variant.product.id)
    colors = ProductVariant.objects.filter(product=product.id).distinct("color").all()
    related_variants = ProductVariant.objects.all().select_related('product').exclude(id=variant.id).reverse()[:4]
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = request.user.carts.all().count()
        wish_count = request.user.wishlist.all().count()
    return render(request, 'detail.html', {"variant": variant, "product": product, "related_variants": related_variants, "reviews":reviews, "colors": colors, "count": reviews.count, "cart_count": cart_count, "wish_count": wish_count, "information": info})

def category(request, cat):
    products = Product.objects.filter(category=cat).all()
    data = []
    for product in products:
        data += ProductVariant.objects.filter(product=product)
    paginator = Paginator(data, 4) # Show 4 items per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'shop.html', {"variants": variants, "cart_count": cart_count, "wish_count": wish_count, "category": True, "information": info})


def searched(request):
    query = request.POST.get('query')
    print(query)
    if query:
        products = Product.objects.filter( Q(title__icontains=query) | Q(short_description__icontains=query) | Q(category__icontains=query) )
    else:
        products = Product.objects.all()
    data = []
    for product in products:
        data += ProductVariant.objects.filter(product=product)
    paginator = Paginator(data, 4) # Show 4 items per page
    page_number = request.GET.get('page')
    variants = paginator.get_page(page_number)
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'shop.html', {"variants": variants, "cart_count": cart_count, "wish_count": wish_count, "category": False, "information": info})


def register(request):
    info = Information.objects.get(id=1)
    if request.method == 'GET':
        context = {'form': RegisterForm(), "information": info} 
        return render(request, 'register.html', context)

    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        context = {'form': form, "information": info}
        return render(request, 'register.html', context)
    
def login_user(request):
    info = Information.objects.get(id=1)
    if request.method == 'GET':
        context = {'form': LoginForm(), "information": info}
        return render(request, 'login.html', context)

    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if not User.objects.filter(email=email).exists():
                form.add_error('email', 'Email does not exist please sign up first!')
            if email and password:
                user = authenticate(request, email=email, password=password)
                if not user:
                    form.add_error('password', 'Invalid password try again!')
                else:
                    login(request, user)
                    return redirect('index')
        context = {'form': form, "information": info}
        return render(request, 'login.html', context)

@login_required
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('index')

@login_required
def profile(request):
    dummy = Addres.objects.filter(user=request.user).all()
    info = Information.objects.get(id=1)
    cart_count = Cart.objects.filter(user=request.user).all().count()
    wish_count = Wishlist.objects.filter(user=request.user).all().count()
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        address2 = request.POST.get('address2')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        country = request.POST.get('country')
        orders = request.POST.get('orders')

        Addres(user=request.user, name=name, email=email, phone=phone, address_line1=address, address_line2=address2, landmark=landmark, city=city, pincode=pincode, state=state, country=country).save()
        if orders == "orders":
            return redirect('checkout')
        return redirect('profile')
    return render(request, 'profile.html', {"addresses": dummy, "cart_count": cart_count, "wish_count": wish_count, "information": info})

@login_required
def remove_address(request, id):
    data = Addres.objects.get(id=id)
    data.delete()
    return redirect('profile')

@login_required
def show_cart(request):
    cart = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 70.0
    total_amount = 0.0
    # cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart:
        for p in cart:
            tempamount = (p.quantity * p.variant.discount_price)
            amount += tempamount
            total_amount = amount + shipping_amount
    info = Information.objects.get(id=1)
    wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'cart.html', {'carts': cart, 'amount': amount, 'shipping': shipping_amount, 'total_amount': total_amount, 'cart_count': cart.count(), "wish_count": wish_count, "information": info})

@login_required
def add_cart(request, id):
    variant = ProductVariant.objects.get(id=id)
    in_cart = Cart.objects.filter(Q(variant=variant.id) & Q(user=request.user)).exists()
    if request.method == 'GET':
        if variant.quantity < 1:
            return HttpResponse('<img src="static/img/sold.avif" width="45" height="45">')
        if not in_cart:
            Cart(variant=variant, user=request.user).save()
        return HttpResponse('<i class="fas fa-check"></i>')
    
    elif request.method == 'POST':
        quantity = request.POST.get('quantity')
        if not in_cart:
            if int(quantity) <= variant.quantity:
                Cart(variant=variant, user=request.user, quantity=quantity).save()
            else:
                Cart(variant=variant, user=request.user, quantity=variant.quantity).save()
        return redirect('product', slug=variant.slug)

@login_required
def plus_cart(request):
    if request.method == 'GET':
        cart_id = request.GET['cart_id']
        c = Cart.objects.get(id=cart_id)
        if c.quantity < c.variant.quantity:
            c.quantity+=1
            c.save()
        else:
            data = {
                'availibility': 'no',
                'quantity': c.variant.quantity
            }
            return JsonResponse(data)
        amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.variant.discount_price)
            amount += tempamount
        data = {
            'quantity': c.quantity,
            'p_amount': (c.variant.discount_price*c.quantity),
            'amount': amount,
            'total_amount': amount + 70.0
        }
        return JsonResponse(data)

@login_required
def minus_cart(request):
    if request.method == 'GET':
        cart_id = request.GET['cart_id']
        c = Cart.objects.get(id=cart_id)
        amount = 0.0
        if c.quantity > 1:
            c.quantity-=1
            c.save()
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            for p in cart_product:
                tempamount = (p.quantity * p.variant.discount_price)
                amount += tempamount
            data = {
                'quantity': c.quantity,
                'p_amount': (c.variant.discount_price*c.quantity),
                'amount': amount,
                'total_amount': amount + 70.0
            }
            return JsonResponse(data)

@login_required
def remove_cart(request, id):
    data = Cart.objects.get(Q(variant=id) & Q(user=request.user))
    data.delete()
    return HttpResponse('')

@login_required
def wishlist(request):
    data = Wishlist.objects.all()
    info = Information.objects.get(id=1)
    cart_count = Cart.objects.filter(user=request.user).all().count()
    wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'wishlist.html', {"wishlists": data, "cart_count": cart_count, "wish_count": wish_count, "information": info})   

@login_required
def addwish(request, id):
    variant = ProductVariant.objects.get(id=id)
    user = request.user
    in_wishlist = Wishlist.objects.filter(Q(variant=variant) & Q(user=user)).exists()
    if not in_wishlist:
        Wishlist(variant=variant, user=user).save()
    return HttpResponse('<i class="fas fa-heart" style="color: red;"></i>')
        
@login_required
def remove_wishlist(request, id):
    data = Wishlist.objects.get(Q(variant=id) & Q(user=request.user))
    data.delete()
    return HttpResponse('')

@login_required
def review(request):
    if request.method == 'POST':
        review = request.POST.get('review')
        rating = request.POST.get('rating')
        prod_id = request.POST.get('product')
        var_id = request.POST.get('variant')
        variant = ProductVariant.objects.get(id=var_id)
        product = Product.objects.get(id=prod_id)
        reviewed = Review.objects.filter(Q(product=product) & Q(user=request.user)).exists()

        if not reviewed:
            Review(product=product, user=request.user, comment=review, rating=rating).save()

    return redirect('product', slug=variant.slug)


@login_required
def checkout(request):
    add = Addres.objects.filter(user=request.user)
    cart_items = Cart.objects.filter(user=request.user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    info = Information.objects.get(id=1)
    cart_count = Cart.objects.filter(user=request.user).all().count()
    wish_count = Wishlist.objects.filter(user=request.user).all().count()

    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.variant.discount_price)
            amount += tempamount
        total_amount = amount + shipping_amount

        payment = razorpay_client.order.create({'amount': total_amount*100, 'currency': 'INR', 'payment_capture': 1})

        return render(request, 'checkout.html', {'addresses':add, 'carts': cart_items, 'payment': payment, 'shipping': shipping_amount, 'total_amount': total_amount, "cart_count": cart_count, "wish_count": wish_count, "information": info})
    else:
        return render(request, 'checkout.html', {'addresses':add, 'carts': cart_items, "cart_count": cart_count, "wish_count": wish_count, "information": info})

@login_required
def payment(request):
    custid = request.GET.get('custid')
    order = request.GET.get('order_id')
    pay_id = request.GET.get('payment_id')
    signature = request.GET.get('signature')
    amount = request.GET.get('amount')
    address = Addres.objects.get(id=custid)
    Payment(user=request.user, address=address,  order_id=order,  payment_id=pay_id, signature=signature, amount=amount).save()
    payment = Payment.objects.get(order_id=order) 
    
    cart = Cart.objects.filter(user=request.user)
    for c in cart:
        Order(user=request.user, variant=c.variant, quantity=c.quantity, payment=payment, price=c.variant.discount_price).save()
        c.variant.quantity = c.variant.quantity - c.quantity
        c.variant.save()
        c.delete()
    return redirect('orders')

@login_required
def user_orders(request):
    data = Payment.objects.filter(user=request.user).all()
    info = Information.objects.get(id=1)
    cart_count = Cart.objects.filter(user=request.user).all().count()
    wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'orders.html', {"payments":data, "cart_count": cart_count, "wish_count": wish_count, "information": info})

def blogs(request):
    data = Blog.objects.all()
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, 'blog.html', {"blogs":data, "cart_count": cart_count, "wish_count": wish_count, "information": info})

def blog_details(request, slug):
    data = Blog.objects.get(slug=slug)
    blogs = BlogDetail.objects.filter(blog=data).all()
    related = Blog.objects.all().prefetch_related("blogs").exclude(id=data.id).reverse()[:7]
    info = Information.objects.get(id=1)
    cart_count = 0
    wish_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    return render(request, "blogdetail.html", {"blog":data, "blogs": blogs, "related": related, "cart_count": cart_count, "wish_count": wish_count, "information": info})

def contact(request):
    cart_count = 0
    wish_count = 0
    info = Information.objects.get(id=1)
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).all().count()
        wish_count = Wishlist.objects.filter(user=request.user).all().count()
    if request.method == 'GET':
        context = {'form': ContactForm(), "information": info, "cart_count": cart_count, "wish_count": wish_count}
        return render(request, 'contact.html', context)

    elif request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')            
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')            
            message = form.cleaned_data.get('message')
            if len(name) < 5 and len(email) < 15:
                form.add_error('name', 'Name is too short!')
                form.add_error('email', 'Email is too short!')
            else:
                text = f'''You have received a message Quilts Shop Pvt. Ltd. website.\nName: {name}\nEmail: {email}\nMessage: {message}'''
                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['shaikharshi69@gmail.com', 'iamaladdin02@gmail.com']
                send_mail(subject=subject, message=text, from_email=email_from, recipient_list=recipient_list)
                messages.success(request, 'Email Sent Successfully')
                return redirect('contact')
        context = {'form': form, "information": info, "cart_count": cart_count, "wish_count": wish_count}
        return render(request, 'contact.html', context)

def subscribe(request):
    if request.method == 'POST':
        to = request.POST.get('email')
        try:
            validate_email(to)
        except ValidationError as e:
            return redirect('index')

        if not Subscription.objects.filter(email=to).exists():
            Subscription(email=to).save()
            info = Information.objects.get(id=1)
            product = ProductVariant.objects.all()[:3]
            html_content = render_to_string('subscribe.html', {'information':info, 'products':product})
            text_content = strip_tags(html_content)
            email = EmailMultiAlternatives(
                'Thank you for subscribing to our website.', 
                text_content,
                settings.EMAIL_HOST_USER,
                [to]
            )
            email.attach_alternative(html_content,'text/html')
            email.send()
    return redirect('index')
