from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Customer, Staff, Driver, Car
from .forms import StaffForm, DriverForm, CarForm

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
    return render(request, "admin_dashboard.html")

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
    return render(request, "staff_dashboard.html")

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
    return render(request, "driver_dashboard.html")





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
