# 🏨 HotelHub - Django Hotel Booking System

HotelHub is a premium, modern, responsive web application for managing room views, reservations, and customer feedback, built with Django.

## ✨ Features

- **User Authentication**: Secure guest registration, login, logout, and profile tracking.
- **Accommodation Discovery**: View rooms styled as grids with capacity tags, average rating badges, and features.
- **Dynamic Search & Filters**: Search rooms by check-in/out date ranges and guest capacity.
- **Live Booking Calculator**: Live date-range validation and total cost calculation (including taxes/fees) using an AJAX backend endpoint.
- **Reservations Dashboard**: Timeline view of upcoming, active, completed, and cancelled bookings.
- **Interactive Reviews**: Allows users who have completed stays to write reviews.
- **Dark/Light Mode**: Elegant theme toggler that persists guest preferences using LocalStorage.

---

## 🛠️ Setup & Installation

1. **Clone the Repository**:
   ```bash
   git clone <your-repository-url>
   cd hotel_booking_system
   ```

2. **Set up Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install django
   ```
   > Note: Additional packages may be required depending on the features you use. Install them as needed.

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Seed Sample Data**:
   Populate the database with test users, rooms, room types, reviews, and bookings:
   ```bash
   python seed_data.py
   ```

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

---

## 👤 Test Accounts

After running `seed_data.py`, you can test the application using:

- **Django Admin Console (`/admin/`)**:
  - Username: `admin`
  - Password: `admin123`

- **Customer Alice** (Has completed stays, can write reviews):
  - Username: `alice`
  - Password: `alice123`

- **Customer Bob** (Has upcoming reservations, can cancel bookings):
  - Username: `bob`
  - Password: `bob123`
