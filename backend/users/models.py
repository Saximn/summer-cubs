
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is a required field")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('medical_staff', 'Medical Staff'),
        ('patient', 'Patient'),
    ]
    
    username = None  # Disable username field
    email = models.EmailField(max_length=20, unique=True)
    birthday = models.DateField(null=True, blank=True)
    fullname = models.CharField(max_length=200)
    role = models.CharField(max_length=30, choices=ROLES, default="patient")
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    capacity = models.IntegerField(default=1)
    floor = models.IntegerField(null=True, blank=True)
    
    def str(self):
        return f"Room {self.room_number} (Capacity: {self.capacity})"
    
class MedicalStaff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    dob = models.DateField(blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    dob = models.DateField()
    
class PatientEntry(models.Model):
    SEVERITY_LEVEL = [
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red')
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    assigned_staff = models.ManyToManyField(MedicalStaff)
    assigned_room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVEL, default="green")
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    
class Feedback(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=3000)

## OPTIONAL FEATURE ##
class FeedbackForStaff(Feedback):
    staff = models.ManyToManyField(MedicalStaff)
