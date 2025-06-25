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
  class Meta:
    model = Room
    fields = ['room_number', 'capacity', 'floor']

class PatientEntrySerializer(serializers.ModelSerializer):
  class Meta:
    model = PatientEntry
    fields = [
      'id',
      'patient', 
      'assigned_staff',
      'assigned_room',
      'severity',
      'entry_time',
      'exit_time',
      'completed'
    ]
