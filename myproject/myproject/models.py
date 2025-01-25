from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


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
    

    
    
    
