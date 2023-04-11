from django.db import models
from datetime import timedelta
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from .helpers import generate_slug, generate_blog_slug, compress_img
from froala_editor.fields import FroalaField


class UserManager(BaseUserManager):
    def create_user(self, name, email, phone, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name = name,
            phone = phone
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            name=name,
            phone=phone,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name  = models.CharField(max_length=225, null=False)
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    phone    = models.CharField(max_length=15, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

product_category = (
    ('Quilts', 'Quilts'),
    ('Bed Covers', 'Bed Covers'),
    ('Bed Sheets', 'Bed Sheets'),
    ('Pillow Covers', 'Pillow Covers'),
    ('Kid Quilts', 'Kid Quilts'),
)

class Product(models.Model):
    title = models.CharField(max_length=500, null=False)
    short_description = models.CharField(max_length=500, blank=True)
    description = FroalaField()
    features = FroalaField()
    category = models.CharField(choices=product_category, max_length=15)
    
    def average_rating(self):
        reviews = self.reviews.all()
        dummy = 0
        for r in reviews:
            dummy += r.rating
        try:
            rating = round(dummy/reviews.count(), 1)
        except ZeroDivisionError:
            rating = 0
        return rating 

    def review_count(self):
        count = self.reviews.all().count()
        return count

    def __str__(self) -> str:
        return str(self.title)
    
class Image(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image =  models.ImageField(upload_to='product-img', help_text='Upload image of size 400 x 400')

    def save(self, *args, **kwargs):
        new = compress_img(self.image)
        self.image = new
        super(Image, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.product.title)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    thumbnail =  models.ImageField(upload_to='product-img', help_text='Upload image of size 400 x 400')
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True)
    quantity = models.PositiveIntegerField(default=5)
    sell_price = models.FloatField(null=False)
    discount_price = models.FloatField(null=False)
    slug = models.SlugField(max_length=500, null=True, blank=True, unique=True)

    def save(self, *args, **kwargs):
        self.slug = generate_slug(f"{self.product.title} {self.color} {self.size}")
        self.color = self.color.capitalize()
        self.size = self.size.capitalize()
        new = compress_img(self.thumbnail)
        self.thumbnail = new
        super(ProductVariant, self).save(*args, **kwargs)

    def discount_percent(self):
        return str(round(((self.discount_price-self.sell_price)/self.sell_price)*100, 2))

    def __str__(self) -> str:
        return str(self.product.title)


class Wishlist(models.Model):
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, related_name='wishlist', on_delete=models.CASCADE)

    def in_cart(self):
        for i in self.user.carts.all():
            if self.variant == i.variant:
                return True
        return False

    def __str__(self) -> str:
        return str(self.user.name)

class Cart(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name='carts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='carts', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def in_wishlist(self):
        for i in self.user.wishlist.all():
            if self.variant == i.variant:
                return True
        return False
    
    @property
    def total_amount(self):
        return self.quantity * self.variant.discount_price
    
    def __str__(self) -> str:
        return str(self.user.name)


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, null=False)
    rating = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.user.name)
    

class Addres(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=15, null=False)
    email = models.EmailField(verbose_name='email address', max_length=255, null=True)
    address_line1 = models.CharField(max_length=255, null=False)
    address_line2 = models.CharField(max_length=255, null=True)
    landmark = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=False)
    pincode = models.CharField(max_length=10, null=False)
    state = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)

    def __str__(self) -> str:
        return str(self.name)

class Payment(models.Model):
    user = models.ForeignKey(User, related_name="payments", on_delete=models.CASCADE)
    address = models.ForeignKey(Addres, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    signature = models.CharField(max_length=100, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    expected_delivery = models.DateTimeField(auto_now_add=True)

    @property
    def discount(self):
        money = 0
        for i in self.orders.all():
            money += i.quantity * (i.variant.sell_price - i.variant.discount_price)
        return money

    def __str__(self) -> str:
        return str(self.user.name)

STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)

class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    variant =  models.ForeignKey(ProductVariant, related_name='orders', on_delete=models.CASCADE)
    payment =  models.ForeignKey(Payment, related_name='orders', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(null=False)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='Pending')

    def save(self, *args, **kwargs):
        self.price = self.variant.discount_price
        super(Order, self).save(*args, **kwargs)

    @property
    def total_amount(self):
        return self.quantity * self.variant.discount_price

    def __str__(self) -> str:
        return str(self.user)

class Blog(models.Model):
    image = models.ImageField(upload_to="blogs", null=False, help_text='Upload image of size 350 x 350')
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50,null=True, blank= True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, null=True, blank=True)
    description =models.TextField()

    def save(self, *args, **kwargs):
        self.slug = generate_blog_slug(self.title)
        new_image = compress_img(self.image)
        self.image = new_image
        super(Blog, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.title)
    
class BlogDetail(models.Model):
    blog = models.ForeignKey(Blog, related_name="blogs", on_delete=models.CASCADE)
    writing = FroalaField()

    def __str__(self) -> str:
        return str(self.blog.title)


class Carousal(models.Model):
    heading = models.CharField(max_length=100, null=True)
    sub_heading = models.CharField(max_length=100, null=True)
    button_link = models.URLField()
    image = models.ImageField(upload_to='carousal')

    def __str__(self) -> str:
        return str(self.heading)


class Offer(models.Model):
    heading = models.CharField(max_length=100, null=True)
    sub_heading = models.CharField(max_length=100, null=True)
    button_link = models.URLField()
    image = models.ImageField(upload_to='offer')

    def __str__(self) -> str:
        return str(self.heading)

class Information(models.Model):
    bio = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    email = models.EmailField(verbose_name='email address', max_length=255)
    phone = models.CharField(max_length=20, null=True)
    twitter = models.CharField(max_length=255, null=True)
    instagram = models.CharField(max_length=255, null=True)
    linkedin = models.CharField(max_length=255, null=True)
    facebook = models.CharField(max_length=255, null=True)

    def __str__(self) -> str:
        return str(self.email)

class Subscription(models.Model):
    email = models.EmailField(verbose_name='email address', max_length=255)

    def __str__(self) -> str:
        return str(self.email)