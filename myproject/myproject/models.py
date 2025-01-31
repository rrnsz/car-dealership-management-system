from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from abc import ABC, abstractmethod



class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

# Custom User Manager
class UserManager(BaseUserManager, metaclass=SingletonMeta):
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
    type = models.CharField(max_length=50, default="sedan")
    transmission = models.CharField(max_length=50, default="automatic")
    gas = models.CharField(max_length=50, default="50")
    power = models.CharField(max_length=50, default="0")
    year = models.CharField(max_length=4, default="2020")

    def __str__(self):
        return f"{self.make} {self.model}"
    

    

class OrderStatusStrategy(ABC):
    @abstractmethod
    def handle_status_change(self, order):
        pass

class PendingStrategy(OrderStatusStrategy):
    def handle_status_change(self, order):
        order.status = 'pending'
        order.driver = None
        order.delivery_date = None

class ProcessingStrategy(OrderStatusStrategy):
    def handle_status_change(self, order, staff, driver, delivery_date):
        order.status = 'processing'
        order.staff = staff
        order.driver = driver
        order.delivery_date = delivery_date

class ShippedStrategy(OrderStatusStrategy):
    def handle_status_change(self, order):
        order.status = 'shipped'

class DeliveredStrategy(OrderStatusStrategy):
    def handle_status_change(self, order):
        order.status = 'delivered'

# Add these observer classes after your imports
class OrderObserver(ABC):
    @abstractmethod
    def update(self, order):
        pass

class StockObserver(OrderObserver):
    def update(self, order):
        if order.status == 'processing':
            car = order.car
            if car.stock > 0:
                car.stock -= 1
                car.save()

class NotificationObserver(OrderObserver):
    def update(self, order):
        if order.status == 'processing':
            # You could implement actual notification logic here
            print(f"Order {order.id} is now being processed")
        elif order.status == 'delivered':
            print(f"Order {order.id} has been delivered")

# Modify the Order model to include the observer pattern
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

    _observers = []
    
    @classmethod
    def add_observer(cls, observer):
        cls._observers.append(observer)
    
    @classmethod
    def remove_observer(cls, observer):
        cls._observers.remove(observer)
    
    def notify_observers(self):
        for observer in self._observers:
            observer.update(self)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if not is_new:  # Only notify on updates, not on creation
            self.notify_observers()

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

    def update_status(self, new_status, **kwargs):
        strategies = {
            'pending': PendingStrategy(),
            'processing': ProcessingStrategy(),
            'shipped': ShippedStrategy(),
            'delivered': DeliveredStrategy()
        }
        
        strategy = strategies.get(new_status)
        if strategy:
            strategy.handle_status_change(self, **kwargs)
            self.save()
        return self


Order.add_observer(StockObserver())
Order.add_observer(NotificationObserver())

class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')

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

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"