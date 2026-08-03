# Car Dealership Management System

A full-stack car dealership management system built with Django. Supports role-based
dashboards for admins, staff, delivery drivers, and customers, with vehicle inventory
management and an end-to-end order/delivery workflow.

## Features

- **Role-based accounts**: custom email-based auth with four roles — Admin, Staff,
  Driver, Customer — each with their own dashboard.
- **Vehicle inventory**: add/edit/delete cars (make, model, category, price, stock,
  transmission, year, etc.) with multiple images per car.
- **Public catalog**: browsable vehicle listing with category filtering and detail pages.
- **Staff & driver management**: admins can add, edit, and remove staff and delivery
  drivers.
- **Order & delivery workflow**: customers place orders; staff confirm and assign a
  driver + delivery date; drivers update delivery status through
  `pending → processing → shipped → delivered`.
- **Contact form**: public inquiries are stored and reviewable by staff.
- **Django admin**: all models are registered for direct data management.

## Design patterns

- **Singleton** — the custom `UserManager`.
- **Strategy** — order status transitions (`PendingStrategy`, `ProcessingStrategy`,
  `ShippedStrategy`, `DeliveredStrategy`).
- **Observer** — stock decrement and notifications react to order status changes
  (`StockObserver`, `NotificationObserver`).

## Tech stack

- Python / Django
- SQLite (default local database)

## Getting started

```bash
cd myproject
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` for the site, or `http://127.0.0.1:8000/admin/`
for the Django admin.

### Configuration

By default `DJANGO_SECRET_KEY` falls back to a local-dev-only key baked into
`settings.py`. For any real deployment, set your own:

```bash
export DJANGO_SECRET_KEY="your-own-secret-key"
```
