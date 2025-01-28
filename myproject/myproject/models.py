from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_migrate
from django.dispatch import receiver


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# Base User Model
class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("staff", "Dealership Staff"),
        ("driver", "Delivery Driver"),
        ("customer", "Customer"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    def __str__(self):
        return self.email

# Admin Model
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100, default="Unknown")

    def __str__(self):
        return self.full_name

# Staff Model
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100, default="Unknown")
    phone_number = models.CharField(max_length=15, default="")

    def __str__(self):
        return self.user.email

# Driver Model
class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100, default="Unknown")
    phone_number = models.CharField(max_length=15, default="")
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.email

# Customer Model
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=100, default="Unknown")
    phone_number = models.CharField(max_length=15, default="")

    def __str__(self):
        return self.full_name
    

# Car Model
class Car(models.Model):  

    CATEGORY_CHOICES = [
        ("american", "American"),
        ("german", "German"),
        ("japanese", "Japanese"),
        ("italian", "Italian"),
    ]

    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) 
    image = models.ImageField(upload_to='car_images/', blank=True, null=True) 
    type = models.CharField(max_length=50, default="sedan")
    transmission = models.CharField(max_length=50, default="automatic")
    gas = models.CharField(max_length=50, default="50")

    def __str__(self):
        return f"{self.make} {self.model}"
    

    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)  
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True) 
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True) 
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  
    address = models.CharField(max_length=255)  
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"Order {self.id} - {self.car.make} {self.car.model}"

    def customer_details(self):
        return f"{self.customer.full_name}, Email: {self.customer.user.email}, Phone: {self.customer.phone_number}"

    def car_details(self):
        return f"{self.car.make} {self.car.model}, Type: {self.car.type}, Price: ${self.car.price}"

    def staff_details(self):
        return f"{self.staff.full_name}, Email: {self.staff.user.email}, Phone: {self.staff.phone_number}"

    def driver_details(self):
        return f"{self.driver.full_name}, License: {self.driver.license_number}, Phone: {self.driver.phone_number}"
    



@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name == 'myproject': 
        User = kwargs['app_config'].get_model('User')
        Admin = kwargs['app_config'].get_model('Admin')
        if not User.objects.filter(email='admin@example.com').exists():
            admin_user = User.objects.create_user(
                email='admin@example.com',
                password='0000',
                role='admin',
                is_staff=True
            )
            Admin.objects.create(user=admin_user, full_name='Admin')
