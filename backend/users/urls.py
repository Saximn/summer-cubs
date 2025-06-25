from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
router.register('users', UserViewset, basename='users')
router.register('patient', PatientViewset, basename="patient")
router.register('patient/entry', PatientEntryViewset, basename="patient_entries")
router.register('room', RoomViewset, basename='room')
router.register('feedback', FeedbackViewset, basename="feedback")
router.register('feedbackforstaff', FeedbackForStaffViewset, basename="feedback_for_staff")

urlpatterns = router.urls
