from django.contrib import admin
from .models import User, Admin, Staff, Driver, Customer, Car, CarImage, Order, ContactMessage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_active", "is_staff", "is_superuser")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email",)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user")


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone_number")


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone_number", "license_number")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "phone_number")


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("make", "model", "category", "type", "year", "price", "stock")
    list_filter = ("category", "type", "transmission")
    search_fields = ("make", "model")
    inlines = [CarImageInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "car", "status", "staff", "driver", "order_date", "delivery_date")
    list_filter = ("status",)
    search_fields = ("customer__full_name", "car__make", "car__model")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")
    search_fields = ("name", "email", "subject")
