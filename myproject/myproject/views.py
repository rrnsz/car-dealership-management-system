from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Customer, Staff, Driver, Car, Order, ContactMessage, CarImage
from .forms import StaffForm, DriverForm, CarForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum

from myproject import models



@login_required
def create_order(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == 'POST':
        try:
            Order.objects.create(
                customer=request.user.customer, 
                car=car,
                address=request.POST.get('address'),
                payment_method=request.POST.get('paymentMethod'),
                status='pending'
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Order created successfully'
                })
            
            return redirect('index')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
            messages.error(request, f"Error creating order: {str(e)}")
            return redirect('car_detail', car_id=car_id)
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
    total_cars = Car.objects.count()  
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
            form.save()  
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
    total_cars = Car.objects.count()  
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


@login_required
def pending_orders(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        order = Order.objects.get(id=order_id)

        if action == 'confirm':
            driver_id = request.POST.get('driver')
            delivery_date = request.POST.get('delivery_date')
            
            
            staff = request.user.staff
            driver = Driver.objects.get(user_id=driver_id)
            
            # Update order details
            order.staff = staff
            order.driver = driver
            order.delivery_date = delivery_date
            order.status = 'processing'
            order.save()
            
            messages.success(request, f'Order #{order_id} has been confirmed and assigned to {driver.full_name}.')
        
        elif action == 'cancel':
            order.status = 'cancelled'
            order.save()
            messages.warning(request, f'Order #{order_id} has been cancelled.')

        return redirect('pending_orders')

    pending_orders = Order.objects.filter(status='pending')
    drivers = Driver.objects.all()
    return render(request, 'pending_orders.html', {
        'pending_orders': pending_orders,
        'drivers': drivers
    })

@login_required
def manage_cars(request):
    cars = Car.objects.all().prefetch_related('images')
    return render(request, "manage_cars.html", {"cars": cars})


@login_required
def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            # Handle multiple images
            images = request.FILES.getlist('images')
            for image in images:
                CarImage.objects.create(car=car, image=image)
            messages.success(request, 'Car added successfully!')
            return redirect('manage_cars')
    else:
        form = CarForm()
    return render(request, 'add_car.html', {'form': form})

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    car.delete()
    messages.success(request, "Car deleted successfully!")
    return redirect('manage_cars')

def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            try:
                
                car = form.save()
                
                # Handle new images if they exist
                new_images = request.FILES.getlist('images')
                if new_images:
                   
                    CarImage.objects.filter(car=car).delete()
                    
                    
                    for image in new_images:
                        CarImage.objects.create(car=car, image=image)
                
                messages.success(request, "Car updated successfully!")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})
                return redirect('manage_cars')
            
            except Exception as e:
                messages.error(request, f"Error updating car: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        else:
            messages.error(request, "Please correct the errors below.")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = CarForm(instance=car)
    
    return render(request, "edit_car.html", {"form": form, "car": car})

def update_delivery_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        current_status = order.status
        
        # Define the status flow
        if current_status == 'processing':
            order.status = 'shipped'
        elif current_status == 'shipped':
            order.status = 'delivered'
        
        order.save()
        messages.success(request, f'Order status updated to {order.status}')
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

    
    return render(request, 'partials/car_list.html', {'cars': cars})

#  ------------------------------------------------------------------------------------------

def contact(request):
    return render(request, 'contact.html')



def car_detail_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    context = {
        'car': car
    }
    
    # Add user information to context
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            context['full_name'] = customer.full_name
        except Customer.DoesNotExist:
            context['full_name'] = request.user.email
            
    return render(request, 'car_detail.html', context)


def submit_inquiry(request, car_id):
    if request.method == 'POST':
        
        messages.success(request, 'Your inquiry has been sent successfully!')
        return redirect('car_detail', car_id=car_id)

def vehicles_view(request):
    category = request.GET.get('category', None)

    if category and category != "all":
        cars = Car.objects.filter(category=category, stock__gt=0)
    else:
        cars = Car.objects.filter(stock__gt=0)

    context = {
        "cars": cars,
        "category": category
    }
    return render(request, "vehicles.html", context)

@login_required
def user_orders(request):
    if request.user.role == 'customer':
        
        active_orders = Order.objects.filter(
            customer=request.user.customer,
            status__in=['pending', 'processing', 'shipped']
        ).exclude(
            status='cancelled'
        ).order_by('-order_date')
        
        
        delivered_orders = Order.objects.filter(
            customer=request.user.customer,
            status='delivered'
        ).order_by('-order_date')
        
        context = {
            'active_orders': active_orders,
            'delivered_orders': delivered_orders,
            'full_name': request.user.customer.full_name
        }
        return render(request, 'user_orders.html', context)
    else:
        messages.error(request, "Access denied.")
        return redirect('index')


def contact_submit(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save the message to database
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully!'
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
def received_messages(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'received_messages.html', {'messages': messages})

def delete_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(ContactMessage, id=message_id)
        message.delete()
        messages.success(request, 'Message deleted successfully!')
    return redirect('received_messages')

def delete_car_image(request, image_id):
    image = get_object_or_404(CarImage, id=image_id)
    car_id = image.car.id
    image.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, "Image deleted successfully!")
    return redirect('edit_car', car_id=car_id)

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