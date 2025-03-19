from django.db import models
from django.contrib.auth.hashers import make_password
import random
import string

# class User_Authentication(models.Model):
#     firstname = models.CharField(max_length = 255)
#     lastname = models.CharField(max_length = 255)
#     email = models.EmailField(unique = True)
#     password1 = models.CharField(max_length = 255)
#     password2 = models.CharField(max_length = 255)
#     password = models.CharField(max_length = 255)
    
#     def save(self, *args, **kwargs):
#         enc = "pbkdf2_sha256$"
#         if not self.password1.startswith(enc):
#             self.password1 = make_password(self.password1)
#         if not self.password2.startswith(enc):
#             self.password2 = make_password(self.password2)
#         if not self.password.startswith(enc):
#             self.password = make_password(self.password)
        
#         super(User_Authentication, self).save(*args, **kwargs)
#     class Meta:
#         db_table = "user_authentication"
        
#     def __str__(self):
#         return self.email
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.contrib.auth.hashers import make_password

class UserAuthenticationManager(BaseUserManager):
    def create_user(self, email, password1, password2, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if password1 != password2:
            raise ValueError("Passwords do not match")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password1)  # Hashing password automatically
        user.password1 = make_password(password1)
        user.password2 = make_password(password2)
        user.password = user.password1  # Storing the same hashed password

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password1, password2, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password1, password2, **extra_fields)

class User_Authentication(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password1 = models.CharField(max_length=255)
    password2 = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # This will store the actual hashed password
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAuthenticationManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'password1', 'password2']

    class Meta:
        db_table = "user_authentication"

    def save(self, *args, **kwargs):
        enc = "pbkdf2_sha256$"
        if not self.password1.startswith(enc):
            self.password1 = make_password(self.password1)
        if not self.password2.startswith(enc):
            self.password2 = make_password(self.password2)
        if not self.password.startswith(enc):
            self.password = make_password(self.password)

        super(User_Authentication, self).save(*args, **kwargs)

    def __str__(self):
        return self.email

    
class Restaurants(models.Model):
    name = models.CharField(max_length = 255)
    location = models.CharField(max_length = 255)
    description = models.TextField()
    images = models.ImageField(upload_to="restaurant_images/", blank = True, null = True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = "RestaurantsList"
        
    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=255)
    
    class Meta:
        db_table = "Category"
    
    def __str__(self):
        return self.name
    
class MenuItems(models.Model):
    restaurant = models.ForeignKey(Restaurants, on_delete = models.CASCADE, related_name = "menu_items")
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True, blank = True)
    name = models.CharField(max_length = 255)
    description = models.TextField()
    price = models.DecimalField(max_digits = 6, decimal_places = 2)
    images = models.ImageField(upload_to = "MenuItems_images/", blank = True, null = True)
    is_available = models.BooleanField(default = True)
    
    class Meta:
        db_table = "MenuItems"
        
class Address(models.Model):
    user = models.ForeignKey(User_Authentication, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)  # Default address flag

    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}"

    class Meta:
        db_table = "Address"

        
import random
import string
from django.db import models

class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("UPI", "UPI"),
            ("Credit Card", "Credit Card"),
            ("Debit Card", "Debit Card"),
            ("Cash on Delivery", "Cash on Delivery")
        ],
        default="UPI",
    )

    status = models.CharField(
        max_length=255,
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled")
        ],
        default="Pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_order_id():
        """Generates a unique Order ID."""
        while True:
            new_order_id = "ORD" + "".join(random.choices(string.digits, k=15))
            if not Order.objects.filter(order_id=new_order_id).exists():
                return new_order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()  # ✅ Fixed function call
        super().save(*args, **kwargs)

    class Meta:
        db_table = "Order"

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
  
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = "order_items")
    menu_item = models.ForeignKey(MenuItems, on_delete = models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)

    class Meta:
        db_table = "OrderItem"
        
    def __str__(self):
        return f"{self.menu_item} x {self.quantity}"
    
class Cart(models.Model):
    user = models.ForeignKey(User_Authentication, on_delete = models.CASCADE, related_name = "user_name")
    item = models.ForeignKey(MenuItems, on_delete = models.CASCADE, related_name = "menu_items")
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = "CartItems"

    def total_price(self):
        return self.quantity * self.item.price

    def __str__(self):
        return f"{self.item.name} ({self.quantity}) - ₹{self.total_price()}"