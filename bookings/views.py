from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, date
from decimal import Decimal
from .models import RoomType, Room, Booking, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def home(request):
    room_types = RoomType.objects.all()
    
    # Extract search parameters
    check_in_str = request.GET.get("check_in")
    check_out_str = request.GET.get("check_out")
    capacity_str = request.GET.get("capacity")
    
    check_in = None
    check_out = None
    capacity = None
    searched = False
    
    if check_in_str and check_out_str:
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            searched = True
            
            if check_in < date.today():
                messages.warning(request, "Check-in date cannot be in the past.")
                searched = False
            elif check_out <= check_in:
                messages.warning(request, "Check-out date must be after the check-in date.")
                searched = False
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            searched = False

    if capacity_str:
        try:
            capacity = int(capacity_str)
            if capacity <= 0:
                capacity = None
        except ValueError:
            capacity = None

    filtered_room_types = []
    for rt in room_types:
        # Check capacity filter
        if capacity and rt.capacity < capacity:
            continue
            
        # Check availability filter if dates provided
        if searched and check_in and check_out:
            # Find if there is at least one room of this type available
            rooms = Room.objects.filter(room_type=rt, is_active=True)
            available = False
            for r in rooms:
                if r.is_available(check_in, check_out):
                    available = True
                    break
            if not available:
                continue
                
        filtered_room_types.append(rt)
        
    context = {
        "room_types": filtered_room_types,
        "check_in": check_in_str if searched else "",
        "check_out": check_out_str if searched else "",
        "capacity": capacity_str or "",
        "searched": searched
    }
    return render(request, "bookings/home.html", context)

def room_detail(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    reviews = room_type.reviews.all()
    
    # Check if user has already stayed in this room type to allow reviewing
    can_review = False
    if request.user.is_authenticated:
        # User has a completed booking for a room of this type
        can_review = Booking.objects.filter(
            user=request.user,
            room__room_type=room_type,
            status__in=["Confirmed", "Completed"]
        ).exists()

    context = {
        "room_type": room_type,
        "reviews": reviews,
        "can_review": can_review,
        "today": date.today().strftime("%Y-%m-%d")
    }
    return render(request, "bookings/room_detail.html", context)

def check_availability_api(request):
    check_in_str = request.GET.get("check_in")
    check_out_str = request.GET.get("check_out")
    room_type_id = request.GET.get("room_type_id")
    
    if not (check_in_str and check_out_str and room_type_id):
        return JsonResponse({"available": False, "error": "Missing parameters"})
        
    try:
        check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        room_type = RoomType.objects.get(pk=room_type_id)
        
        if check_in < date.today() or check_out <= check_in:
            return JsonResponse({"available": False, "error": "Invalid dates"})
            
        # Find operational rooms of this type
        rooms = Room.objects.filter(room_type=room_type, is_active=True)
        available_room = None
        for r in rooms:
            if r.is_available(check_in, check_out):
                available_room = r
                break
                
        nights = (check_out - check_in).days
        total_price = room_type.base_price * nights
        
        if available_room:
            return JsonResponse({
                "available": True,
                "nights": nights,
                "total_price": float(total_price),
                "room_id": available_room.id
            })
        else:
            return JsonResponse({"available": False, "error": "No rooms available for selected dates"})
            
    except (ValueError, RoomType.DoesNotExist):
        return JsonResponse({"available": False, "error": "Invalid data"})

@login_required
def create_booking(request):
    if request.method == "POST":
        room_type_id = request.POST.get("room_type_id")
        check_in_str = request.POST.get("check_in")
        check_out_str = request.POST.get("check_out")
        
        if not (room_type_id and check_in_str and check_out_str):
            messages.error(request, "Please fill in all booking details.")
            return redirect("home")
            
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
            room_type = get_object_or_404(RoomType, pk=room_type_id)
            
            if check_in < date.today():
                messages.error(request, "Check-in date cannot be in the past.")
                return redirect("room_detail", pk=room_type_id)
            if check_out <= check_in:
                messages.error(request, "Check-out date must be after check-in.")
                return redirect("room_detail", pk=room_type_id)
                
            # Find an available room
            rooms = Room.objects.filter(room_type=room_type, is_active=True)
            available_room = None
            for r in rooms:
                if r.is_available(check_in, check_out):
                    available_room = r
                    break
                    
            if not available_room:
                messages.error(request, f"Sorry, no rooms of type '{room_type.name}' are available for the selected dates.")
                return redirect("room_detail", pk=room_type_id)
                
            # Calculate total price
            nights = (check_out - check_in).days
            total_price = room_type.base_price * nights
            
            # Create Booking
            booking = Booking.objects.create(
                user=request.user,
                room=available_room,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price,
                status="Confirmed"
            )
            messages.success(request, f"Booking confirmed! Room {available_room.room_number} booked successfully.")
            return redirect("profile")
            
        except ValueError:
            messages.error(request, "Invalid dates submitted.")
            return redirect("home")
    return redirect("home")

@login_required
def cancel_booking(request):
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
        
        if booking.can_be_cancelled:
            booking.status = "Cancelled"
            booking.save()
            messages.success(request, f"Booking #{booking.id} has been cancelled successfully.")
        else:
            messages.error(request, "This booking cannot be cancelled.")
            
    return redirect("profile")

@login_required
def add_review(request):
    if request.method == "POST":
        room_type_id = request.POST.get("room_type_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        
        room_type = get_object_or_404(RoomType, pk=room_type_id)
        
        # Check review permission
        can_review = Booking.objects.filter(
            user=request.user,
            room__room_type=room_type,
            status__in=["Confirmed", "Completed"]
        ).exists()
        
        if not can_review:
            messages.error(request, "You can only review room types that you have booked.")
            return redirect("room_detail", pk=room_type_id)
            
        try:
            rating_val = int(rating)
            if rating_val < 1 or rating_val > 5:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Invalid rating value.")
            return redirect("room_detail", pk=room_type_id)
            
        Review.objects.create(
            user=request.user,
            room_type=room_type,
            rating=rating_val,
            comment=comment
        )
        messages.success(request, "Thank you! Your review has been submitted.")
        return redirect("room_detail", pk=room_type_id)
        
    return redirect("home")

@login_required
def user_profile(request):
    bookings = Booking.objects.filter(user=request.user)
    
    # Auto-update status for completed bookings (simple background updater simulation)
    today = date.today()
    for b in bookings.filter(status="Confirmed"):
        if b.check_out <= today:
            b.status = "Completed"
            b.save()
            
    active_count = bookings.filter(status__in=["Pending", "Confirmed"]).count()
    completed_count = bookings.filter(status="Completed").count()
    cancelled_count = bookings.filter(status="Cancelled").count()
    
    context = {
        "bookings": bookings,
        "active_count": active_count,
        "completed_count": completed_count,
        "cancelled_count": cancelled_count
    }
    return render(request, "bookings/profile.html", context)

# User Authentication Views
def register_user(request):
    if request.user.is_authenticated:
        return redirect("profile")
        
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to HotelHub Hotels.")
            return redirect("profile")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
        
    return render(request, "bookings/register.html", {"form": form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect("profile")
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect("profile")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, "bookings/login.html", {"form": form})

def logout_user(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect("home")
