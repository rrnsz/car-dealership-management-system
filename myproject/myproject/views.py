from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Customer, Staff, Driver, Car, Order
from .forms import StaffForm, DriverForm, CarForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum

from myproject import models



@login_required
def create_order(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        Order.objects.create(
            customer=request.user.customer, 
            car=car,
            address=request.POST.get('address'),
            payment_method=request.POST.get('paymentMethod'),
            status='pending'
        )
        return redirect('index') 
    else:
        return render(request, 'car_detail.html', {'car': car})
    
# Authentication Views ------------------------------------------------------------------------------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "staff":
                return redirect("staff_dashboard")
            elif user.role == "driver":
                return redirect("driver_dashboard")
            elif user.role == "customer":
                return redirect("index")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("register")

        user = User.objects.create_user(
            email=email,
            password=password,
            role="customer" 
        )

        Customer.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "login.html")





def logout_view(request):

    logout(request)
    
    return redirect("login")


# Admin Dashboard Views ------------------------------------------------------------------------------------------
def admin_dashboard(request):
    total_cars = Car.objects.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    total_staff = Staff.objects.count()
    total_drivers = Driver.objects.count()

    context = {
        'total_cars': total_cars,
        'total_staff': total_staff,
        'total_drivers': total_drivers,
    }

    return render(request, "admin_dashboard.html", context)

# Staff Management Views ------------------------------------------------------------------------------------------
def manage_staff(request):
    staff_list = Staff.objects.all()  
    return render(request, "manage_staff.html", {"staff_list": staff_list})


def add_staff(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")

        if not all([full_name, email, phone_number, password]):
            messages.error(request, "All fields are required.")
            return redirect("add_staff")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("add_staff")

        user = User.objects.create_user(
            email=email,
            password=password,
            role="staff"
        )

        Staff.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number
        )

        messages.success(request, "Staff member added successfully!")
        return redirect("manage_staff")
    else:
        form = StaffForm()
    return render(request, "add_staff.html", {"form": form})


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    if request.method == "POST":
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()  # This will save both User and Staff models
            messages.success(request, "Staff member updated successfully!")
            return redirect("manage_staff")
    else:
        form = StaffForm(initial={
            'full_name': staff.full_name,
            'email': staff.user.email,
            'phone_number': staff.phone_number,
        })
    return render(request, "edit_staff.html", {"form": form})

def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, user_id=staff_id)
    user = staff.user
    staff.delete() 
    user.delete()  
    messages.success(request, "Staff member deleted successfully!")
    return redirect("manage_staff")



# Driver Management Views ------------------------------------------------------------------------------------------
def manage_drivers(request):
    driver_list = Driver.objects.all() 
    return render(request, "manage_driver.html", {"driver_list": driver_list})

def add_driver(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        license_number = request.POST.get("license_number")

        if not all([full_name, email, phone_number, password, license_number]):
            messages.error(request, "All fields are required.")
            return redirect("add_driver")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("add_driver")

        user = User.objects.create_user(
            email=email,
            password=password,
            role="driver"
        )

        Driver.objects.create(
            user=user,
            full_name=full_name,
            phone_number=phone_number,
            license_number=license_number
        )

        messages.success(request, "Driver added successfully!")
        return redirect("manage_drivers")
    else:
        form = DriverForm()
    return render(request, "add_driver.html", {"form": form})



def edit_driver(request, driver_id):
    driver = get_object_or_404(Driver, user_id=driver_id)
    if request.method == "POST":
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save() 
            messages.success(request, "Driver updated successfully!")
            return redirect("manage_drivers")
    else:
        form = DriverForm(initial={
            'full_name': driver.full_name,
            'email': driver.user.email,
            'phone_number': driver.phone_number,
            'license_number': driver.license_number,
        })
    return render(request, "edit_driver.html", {"form": form})

def delete_driver(request, driver_id):
    driver = get_object_or_404(Driver, user_id=driver_id)
    user = driver.user  
    driver.delete()  
    user.delete()  
    messages.success(request, "Driver deleted successfully!")
    return redirect("manage_drivers")





# Staff ------------------------------------------------------------------------------------------
def staff_dashboard(request):
    total_cars = Car.objects.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    total_orders = Order.objects.count()
    total_drivers = Driver.objects.count()

    context = {
        'inventory_count': total_cars,
        'total_orders': total_orders,
        'total_drivers': total_drivers,
    }

    return render(request, "staff_dashboard.html", context)

def orders_history(request):

    completed_orders = Order.objects.exclude(status='pending')
    
    return render(request, 'orders_history.html', {
        'completed_orders': completed_orders,
    })


def pending_orders(request):
    pending_orders = Order.objects.filter(status='pending')
    drivers = Driver.objects.all()

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        driver_user_id = request.POST.get('driver')  
        delivery_date = request.POST.get('delivery_date')


        if not order_id or not driver_user_id:
            raise ValueError("Order ID or Driver User ID is missing or invalid.")

        try:
            driver_user_id = int(driver_user_id)
        except (ValueError, TypeError):
            raise ValueError("Driver User ID must be a valid integer.")

        order = get_object_or_404(Order, id=order_id)
        driver = get_object_or_404(Driver, user_id=driver_user_id)  

        order.staff = request.user.staff
        order.driver = driver
        order.delivery_date = delivery_date
        order.status = 'processing'
        order.save()

        return redirect('pending_orders')

    return render(request, 'pending_orders.html', {
        'pending_orders': pending_orders,
        'drivers': drivers,
    })

def manage_cars(request):
    cars = Car.objects.all()
    return render(request, "manage_cars.html", {"cars": cars})


def add_car(request):
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Car added successfully!")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect("manage_cars")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CarForm()
    return render(request, "add_car.html", {"form": form})

def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Car updated successfully!")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect("manage_cars")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = CarForm(instance=car)
    return render(request, "edit_car.html", {"form": form})
    

# Driver ------------------------------------------------------------------------------------------


def driver_dashboard(request):
    driver = Driver.objects.get(user=request.user)
    
    orders = Order.objects.filter(driver=driver)
    
    active_deliveries = orders.exclude(status='delivered')
    completed_deliveries = orders.filter(status='delivered')
    
    context = {
        'driver': driver,
        'active_deliveries': active_deliveries,
        'completed_deliveries': completed_deliveries,
        'in_progress_count': active_deliveries.filter(Q(status='processing') | Q(status='shipped')).count(),
        'completed_count': completed_deliveries.count(),
    }
    
    return render(request, "driver_dashboard.html", context)



def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
    return redirect('driver_dashboard')

#  ------------------------------------------------------------------------------------------


def index(request):
    category = request.GET.get('category', None)

    if category and category != "all":
        cars = Car.objects.filter(category=category, stock__gt=0)
    else:
        cars = Car.objects.filter(stock__gt=0)

    context = {"cars": cars}

    if request.user.is_authenticated and request.user.role == "customer":
        try:
            customer = Customer.objects.get(user=request.user)
            context['full_name'] = customer.full_name
        except Customer.DoesNotExist:
            context['full_name'] = "Customer"

    return render(request, "index.html", context)


def filter_cars(request):
    category = request.GET.get('category', None)

    if category and category != "all":
        cars = Car.objects.filter(category=category, stock__gt=0)
    else:
        cars = Car.objects.filter(stock__gt=0)

    # Render only the car section as HTML
    return render(request, 'partials/car_list.html', {'cars': cars})

#  ------------------------------------------------------------------------------------------

def contact(request):
    return render(request, 'contact.html')



def car_detail_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    context = {
        'car': car
    }
    return render(request, 'car_detail.html', context)



def submit_inquiry(request, car_id):
    if request.method == 'POST':
        # Here you can add code to handle the form submission
        # For example, sending an email or saving to database
        messages.success(request, 'Your inquiry has been sent successfully!')
        return redirect('car_detail', car_id=car_id)
