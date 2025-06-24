from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from knox import views as know_views
from .views import *

router = DefaultRouter()

router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
router.register('users', UserViewset, basename='users')

urlpatterns = router.urls + [
    path('user/me/', UserMeView.as_view(), name='user-me'),
    path('logout/', know_views.LogoutView.as_view(), name='logout'),
]
