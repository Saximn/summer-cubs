from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from knox import views as know_views
from .views import *

router = DefaultRouter()

router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
router.register('users', UserViewset, basename='users')
router.register('patient', PatientViewset, basename="patient")
router.register('patient_entry', PatientEntryViewset, basename="patient_entries")
router.register('room', RoomViewset, basename='room')

urlpatterns = router.urls + [
    path('user/me/', UserMeView.as_view(), name='user-me'),
    path('logout/', know_views.LogoutView.as_view(), name='logout'),
]
