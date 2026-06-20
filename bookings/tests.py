from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from .models import RoomType, Room, Booking, Review

class RoomAvailabilityTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        # Create RoomType
        self.room_type = RoomType.objects.create(
            name="Test Deluxe",
            description="Test Description",
            capacity=2,
            base_price=Decimal("100.00"),
            features="WiFi, TV",
            image_url="/static/test.png"
        )
        
        # Create Room
        self.room = Room.objects.create(
            room_number="101",
            room_type=self.room_type,
            is_active=True
        )

    def test_room_availability_no_bookings(self):
        """Room should be available when there are no bookings at all."""
        today = date.today()
        checkout = today + timedelta(days=3)
        self.assertTrue(self.room.is_available(today, checkout))

    def test_room_availability_with_booking(self):
        """Room should not be available for dates overlapping with an existing booking."""
        today = date.today()
        booking_start = today + timedelta(days=5)
        booking_end = today + timedelta(days=10)
        
        # Create booking
        Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=booking_start,
            check_out=booking_end,
            total_price=Decimal("500.00"),
            status="Confirmed"
        )
        
        # Test full overlap
        self.assertFalse(self.room.is_available(booking_start + timedelta(days=1), booking_end - timedelta(days=1)))
        
        # Test overlap start
        self.assertFalse(self.room.is_available(booking_start - timedelta(days=2), booking_start + timedelta(days=2)))
        
        # Test overlap end
        self.assertFalse(self.room.is_available(booking_end - timedelta(days=2), booking_end + timedelta(days=2)))
        
        # Test exact overlap
        self.assertFalse(self.room.is_available(booking_start, booking_end))
        
        # Test boundaries (check_out of old is check_in of new)
        self.assertTrue(self.room.is_available(today, booking_start))
        self.assertTrue(self.room.is_available(booking_end, booking_end + timedelta(days=3)))
        
        # Test completely separate future dates
        self.assertTrue(self.room.is_available(booking_end + timedelta(days=5), booking_end + timedelta(days=10)))

    def test_room_availability_with_cancelled_booking(self):
        """Room should be available if overlapping booking is cancelled."""
        today = date.today()
        booking_start = today + timedelta(days=5)
        booking_end = today + timedelta(days=10)
        
        # Create cancelled booking
        Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=booking_start,
            check_out=booking_end,
            total_price=Decimal("500.00"),
            status="Cancelled"
        )
        
        # Should be available despite the overlapping dates
        self.assertTrue(self.room.is_available(booking_start, booking_end))

class BookingDurationAndPriceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.room_type = RoomType.objects.create(
            name="Test Deluxe",
            description="Test Description",
            capacity=2,
            base_price=Decimal("150.00"),
            features="WiFi, TV"
        )
        self.room = Room.objects.create(room_number="102", room_type=self.room_type)

    def test_duration_and_cancellation_properties(self):
        check_in = date.today() + timedelta(days=2)
        check_out = date.today() + timedelta(days=5)
        
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=check_in,
            check_out=check_out,
            total_price=Decimal("450.00"),
            status="Confirmed"
        )
        
        # Test nights calculation (5 - 2 = 3 nights)
        self.assertEqual(booking.duration_nights, 3)
        
        # Test can_be_cancelled property
        self.assertTrue(booking.can_be_cancelled)
        
        # Test cancellation block if in the past/today
        booking.check_in = date.today()
        booking.save()
        self.assertFalse(booking.can_be_cancelled)
        
        # Test cancellation block if status is already Cancelled
        booking.check_in = date.today() + timedelta(days=2)
        booking.status = "Cancelled"
        booking.save()
        self.assertFalse(booking.can_be_cancelled)

class ViewAccessControlTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="customer", password="password123")

    def test_profile_redirects_for_anonymous(self):
        """Profile view should redirect anonymous user to login."""
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_profile_loads_for_authenticated(self):
        """Profile view should render successfully for authenticated user."""
        self.client.login(username="customer", password="password123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/profile.html")
