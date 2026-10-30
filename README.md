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

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Database**: SQLite (default; easy to switch to PostgreSQL)
- **Auth**: Django built-in authentication

---

## 🛠️ Setup & Installation

**Recommended:** Python 3.10 or higher.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Prem-Yelwande/hotel_booking_system.git
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
   pip install -r requirements.txt
   ```
   > The `requirements.txt` pins Django to `>=4.2,<6` for compatibility. Additional packages can be added as needed.

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

> **Note:** `db.sqlite3` is listed in `.gitignore` and is not committed. After cloning you must always run `migrate` and `seed_data.py` to create a fresh local database.

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

## Notes

- Static room images live under `bookings/static/bookings/images/`.
- The project uses the default SQLite database (`db.sqlite3`) which is created automatically on the first `migrate`.
- SQLite is perfect for local development and demos; switch to PostgreSQL for production.

## Development Tips

- Always use a virtual environment and install from `requirements.txt` for consistent setups across machines.
- In production, change the default test account passwords and prefer environment variables for any sensitive configuration.
- SQLite works well for local development; consider PostgreSQL when deploying.
- Use `python manage.py createsuperuser` to create additional admin accounts if needed beyond the seeded test users.
- Run `python manage.py check` before deploying to catch configuration issues early.
- **Production reminder:** Set `DEBUG = False`, configure `ALLOWED_HOSTS`, and use a proper secret key from environment variables before deploying.

## Project Structure

- `bookings/` — Django app containing models, views, templates, static files, and tests.
- `hotel_booking_project/` — Project-level settings, URLs, and WSGI/ASGI configuration.
- `seed_data.py` — Script that populates the database with realistic sample data for testing.
- `manage.py` — Django's command-line utility for administrative tasks.

## Running Tests

```bash
python manage.py test
```

This runs the unit tests located in `bookings/tests.py`. Use `python manage.py test bookings` to run only the bookings app tests.

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'django'`, activate your virtual environment and reinstall from `requirements.txt`.
- For a clean database reset: delete `db.sqlite3`, then re-run `python manage.py migrate` and `python seed_data.py`.
- Ensure Python 3.10+ is used for best compatibility with Django 4.2+/5.x.
- If static files are missing in the browser, run `python manage.py collectstatic` (useful when deploying).

## Security Note

The test accounts above use simple passwords for local development only. Never use these credentials in production. Always change default passwords and use strong, unique credentials, preferably managed via environment variables or a secrets manager.

## Contributing

Contributions are welcome! Small improvements, bug fixes, and documentation updates are appreciated. Please open a pull request with a clear description of the change.
