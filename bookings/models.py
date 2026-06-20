from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.PositiveIntegerField(help_text="Maximum occupancy of the room")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night")
    features = models.TextField(help_text="Comma-separated list of features/amenities")
    image_url = models.CharField(max_length=255, default="/static/bookings/images/deluxe.jpg")

    def __str__(self):
        return self.name

    def get_features_list(self):
        return [f.strip() for f in self.features.split(",") if f.strip()]

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0.0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

class Room(models.Model):
    room_number = models.CharField(max_length=20, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="rooms")
    is_active = models.BooleanField(default=True, help_text="Whether this room is physically operational")

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name})"

    def is_available(self, check_in_date, check_out_date):
        """
        Check if this room is available during the given dates.
        A room is available if there are no bookings that overlap with the range.
        Overlap check: booking.check_in < check_out and booking.check_out > check_in
        """
        overlapping_bookings = self.bookings.filter(
            ~Q(status="Cancelled"),
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        )
        return not overlapping_bookings.exists()

class Booking(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
        ("Completed", "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Confirmed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-check_in"]

    def __str__(self):
        return f"Booking #{self.id} - Room {self.room.room_number} for {self.user.username}"

    @property
    def duration_nights(self):
        delta = self.check_out - self.check_in
        return max(delta.days, 1)

    @property
    def can_be_cancelled(self):
        # Can only cancel if booking starts in the future and isn't already cancelled
        return self.status in ["Pending", "Confirmed"] and self.check_in > date.today()

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} on {self.room_type.name} ({self.rating}/5)"
