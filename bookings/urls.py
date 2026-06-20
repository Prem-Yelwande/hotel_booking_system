from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<int:pk>/", views.room_detail, name="room_detail"),
    path("api/check-availability/", views.check_availability_api, name="check_availability_api"),
    path("booking/create/", views.create_booking, name="create_booking"),
    path("booking/cancel/", views.cancel_booking, name="cancel_booking"),
    path("review/add/", views.add_review, name="add_review"),
    path("profile/", views.user_profile, name="profile"),
    path("register/", views.register_user, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
]
