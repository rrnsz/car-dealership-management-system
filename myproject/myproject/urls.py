from django.contrib import admin
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('driver-dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('update-delivery-status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('logout/', views.logout_view, name='logout'),

    # Staff Management URLs
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('edit-staff/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('delete-staff/<int:staff_id>/', views.delete_staff, name='delete_staff'),

    # Driver Management URLs
    path('manage-drivers/', views.manage_drivers, name='manage_drivers'),
    path('add-driver/', views.add_driver, name='add_driver'),
    path('edit-driver/<int:driver_id>/', views.edit_driver, name='edit_driver'),
    path('delete-driver/<int:driver_id>/', views.delete_driver, name='delete_driver'),

    # Car Management URLs
    path('pending-orders/', views.pending_orders, name='pending_orders'),
    path('orders_history/', views.orders_history, name='orders_history'),
    path('manage-cars/', views.manage_cars, name='manage_cars'),
    path('add-car/', views.add_car, name='add_car'),
    path('edit-car/<int:car_id>/', views.edit_car, name='edit_car'),
    path('delete-car/<int:car_id>/', views.delete_car, name='delete_car'),
    path('filter-cars/', views.filter_cars, name='filter_cars'),
    path('contact/', views.contact, name='contact'),
    path('car/<int:car_id>/', views.car_detail_view, name='car_detail'),
    path('create-order/<int:car_id>/', views.create_order, name='create_order'),
    path('vehicles/', views.vehicles_view, name='vehicles'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('staff/messages/', views.received_messages, name='received_messages'),
    path('staff/messages/delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('delete-car-image/<int:image_id>/', views.delete_car_image, name='delete_car_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
