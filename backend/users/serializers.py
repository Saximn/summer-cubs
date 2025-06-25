from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'email', 'password', 'fullname', 'birthday')
    extra_kwargs = { 'password': {'write_only' : True}}
    
  def create(self, validated_data):
    user = User.objects.create_user(**validated_data)
    return user
 

class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField()
  
  def to_representation(self, instance):
    ret = super().to_representation(instance)
    ret.pop('password', None)
    return ret

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'email', 'fullname', 'role', 'birthday']

class PatientSerializer(serializers.ModelSerializer):
  class Meta:
    model = Patient
    fields = ['id', 'name', 'dob']
    
class MedicalStaffSerializer(serializers.ModelSerializer):
  class Meta:
    model = MedicalStaff
    fields = ['id', 'name', 'dob', 'role']
  
class RoomSerializer(serializers.ModelSerializer):
  current_occupants = serializers.SerializerMethodField()
  class Meta:
    model = Room
    fields = ['room_number', 'capacity', 'floor', 'current_occupants']

  def get_current_occupants(self, obj):
    entries = PatientEntry.objects.filter(assigned_room=obj, completed=False)
    return [
      {
        'id': entry.patient.id,
        'name': entry.patient.name
      }
      for entry in entries
    ]

class PatientEntrySerializer(serializers.ModelSerializer):
  patient_name = serializers.CharField(source='patient.name', read_only=True)
  room_number = serializers.CharField(source='assigned_room.room_number', read_only=True)
  floor = serializers.IntegerField(source='assigned_room.floor', read_only=True)

  class Meta:
    model = PatientEntry
    fields = [
      'id',
      'patient', 
      'patient_name',
      'assigned_staff',
      'assigned_room',
      'room_number',
      'floor',
      'severity',
      'entry_time',
      'exit_time',
      'completed'
    ]
