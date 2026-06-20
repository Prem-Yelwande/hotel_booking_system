from django.contrib import admin
from .models import RoomType, Room, Booking, Review

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "base_price", "average_rating")
    search_fields = ("name", "description")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "is_active")
    list_filter = ("room_type", "is_active")
    search_fields = ("room_number",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "check_in", "check_out", "total_price", "status")
    list_filter = ("status", "check_in", "check_out")
    search_fields = ("user__username", "room__room_number")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "room_type", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "room_type__name", "comment")
