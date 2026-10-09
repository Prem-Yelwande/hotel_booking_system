import os
import django
from datetime import date, timedelta

# Initialize Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hotel_booking_project.settings")
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from bookings.models import RoomType, Room, Booking, Review

def seed_database():
    # Deletes and inserts must succeed together. Without this, a later
    # create failure would leave the database empty after the wipe.
    with transaction.atomic():
        print("Clearing existing data...")
        Booking.objects.all().delete()
        Review.objects.all().delete()
        Room.objects.all().delete()
        RoomType.objects.all().delete()
        User.objects.all().delete()

        print("Creating administrative and test users...")
        # Admin / Staff
        admin_user = User.objects.create_superuser("admin", "admin@hotelhub.com", "admin123")
        # Customers
        alice = User.objects.create_user("alice", "alice@example.com", "alice123")
        bob = User.objects.create_user("bob", "bob@example.com", "bob123")

        print("Creating Room Types...")
        deluxe_type = RoomType.objects.create(
            name="Deluxe Room",
            description="Sleek and luxurious modern hotel room featuring a premium queen size bed, warm ambient lighting, elegant wood paneling, and large windows opening up to our beautifully manicured gardens. Includes a fully stocked minibar and standard luxury amenities.",
            capacity=2,
            base_price=150.00,
            features="Free WiFi, Queen Bed, Garden View, AC, Smart TV, Mini Bar",
            image_url="/static/bookings/images/deluxe.png"
        )

        suite_type = RoomType.objects.create(
            name="Executive Suite",
            description="Spacious luxury suite designed for business and leisure. Features a separate private lounge area with a plush sofa, dining desk, large king size bed, warm custom lighting, and panoramic city views. Indulge in our premium bath amenities.",
            capacity=3,
            base_price=280.00,
            features="Free WiFi, King Bed, Lounge Area, City View, AC, 2x Smart TV, Mini Bar, Bathtub",
            image_url="/static/bookings/images/suite.png"
        )

        penthouse_type = RoomType.objects.create(
            name="Presidential Penthouse",
            description="The absolute pinnacle of luxury. Located on the highest floor, this massive penthouse features floor-to-ceiling glass walls, a private infinity pool on the wrap-around terrace, panoramic ocean and sunset views, minimalist designer furniture, and a private butler service.",
            capacity=4,
            base_price=750.00,
            features="Free WiFi, 2x King Bed, Private Infinity Pool, Ocean View, Sunset Terrace, AC, Home Theater, Bar & Kitchenette, Butler Service",
            image_url="/static/bookings/images/penthouse.png"
        )

        print("Creating Rooms...")
        # Deluxe rooms (100s)
        deluxe_rooms = []
        for num in ["101", "102", "103", "104"]:
            r = Room.objects.create(room_number=num, room_type=deluxe_type, is_active=True)
            deluxe_rooms.append(r)

        # Suite rooms (200s)
        suite_rooms = []
        for num in ["201", "202", "203"]:
            r = Room.objects.create(room_number=num, room_type=suite_type, is_active=True)
            suite_rooms.append(r)

        # Penthouse rooms (500s)
        penthouse_rooms = []
        for num in ["501"]:
            r = Room.objects.create(room_number=num, room_type=penthouse_type, is_active=True)
            penthouse_rooms.append(r)

        print("Creating mock bookings and reviews...")
        # Completed Booking 1: Alice stayed in Deluxe Room 101 in the past
        check_in_1 = date.today() - timedelta(days=8)
        check_out_1 = date.today() - timedelta(days=5)
        booking1 = Booking.objects.create(
            user=alice,
            room=deluxe_rooms[0],
            check_in=check_in_1,
            check_out=check_out_1,
            total_price=deluxe_type.base_price * (check_out_1 - check_in_1).days,
            status="Completed"
        )
        # Review for Deluxe Room type
        Review.objects.create(
            user=alice,
            room_type=deluxe_type,
            rating=5,
            comment="Absolutely stunning! The room was spotless, the bed felt like sleeping on a cloud, and the garden view was so peaceful. Will definitely come back."
        )

        # Completed Booking 2: Bob stayed in Executive Suite 201 in the past
        check_in_2 = date.today() - timedelta(days=6)
        check_out_2 = date.today() - timedelta(days=3)
        booking2 = Booking.objects.create(
            user=bob,
            room=suite_rooms[0],
            check_in=check_in_2,
            check_out=check_out_2,
            total_price=suite_type.base_price * (check_out_2 - check_in_2).days,
            status="Completed"
        )
        # Review for Executive Suite type
        Review.objects.create(
            user=bob,
            room_type=suite_type,
            rating=4,
            comment="Excellent service and the city view at night was incredible. Very spacious lounge area. Docked one star because the minibar restocking was a bit slow, but overall fantastic stay."
        )

        # Completed Booking 3: Alice stayed in Presidential Penthouse 501 in the past
        check_in_3 = date.today() - timedelta(days=4)
        check_out_3 = date.today() - timedelta(days=1)
        booking3 = Booking.objects.create(
            user=alice,
            room=penthouse_rooms[0],
            check_in=check_in_3,
            check_out=check_out_3,
            total_price=penthouse_type.base_price * (check_out_3 - check_in_3).days,
            status="Completed"
        )
        # Review for Presidential Penthouse type
        Review.objects.create(
            user=alice,
            room_type=penthouse_type,
            rating=5,
            comment="Once in a lifetime experience. The private infinity pool during sunset is indescribable. Worth every single penny. World class service!"
        )

        # Active Booking 4: Future reservation for Bob in Deluxe Room 102
        check_in_4 = date.today() + timedelta(days=5)
        check_out_4 = date.today() + timedelta(days=9)
        booking4 = Booking.objects.create(
            user=bob,
            room=deluxe_rooms[1],
            check_in=check_in_4,
            check_out=check_out_4,
            total_price=deluxe_type.base_price * (check_out_4 - check_in_4).days,
            status="Confirmed"
        )

        # Active Booking 5: Future reservation for Alice in Executive Suite 202
        check_in_5 = date.today() + timedelta(days=12)
        check_out_5 = date.today() + timedelta(days=15)
        booking5 = Booking.objects.create(
            user=alice,
            room=suite_rooms[1],
            check_in=check_in_5,
            check_out=check_out_5,
            total_price=suite_type.base_price * (check_out_5 - check_in_5).days,
            status="Confirmed"
        )

        # Reference unused locals so a linter does not flag the demo records.
        _ = (admin_user, booking1, booking2, booking3, booking4, booking5)

    print("Database seeding completed successfully!")
    print("Superuser: username=admin, password=admin123")
    print("Customer 1: username=alice, password=alice123")
    print("Customer 2: username=bob, password=bob123")

if __name__ == "__main__":
    seed_database()
