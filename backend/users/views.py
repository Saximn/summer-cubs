
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *
from .models import *

User = get_user_model()

# Create your views here.
class RegisterViewset(viewsets.ViewSet):
  permission_classes = [permissions.AllowAny]
  queryset = User.objects.all()
  serializer_class = RegisterSerializer
  
  def create(self, request):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    else:
      return Response(serializer.errors, status=400)
    
class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, email=email, password=password)
            if user:
                _, token=AuthToken.objects.create(user)
                return Response(
                {
                    "user": self.serializer_class(user).data,
                    "token": token
                }
                )
            else:
                return Response({"error": "Inavlid credentials"}, status=401)
        else:
            return Response(serializer.errors, status=400)
     
class UserViewset(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def list(self, request):
        queryset = self.queryset
        serializer  = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
  
class PatientEntryViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = PatientEntry.objects.all()
    serializer_class = PatientEntrySerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['POST'], url_path="assign_room")
    def assign_room(self, request, pk=None):
        patient_entry = self.get_object()
        serializer = self.serializer_class(patient_entry)
        if not patient_entry:
            return Response({"error": "Invalid Patient Entry ID"}, status=400)
        assigned_room = Room.objects.get(room_number=request.data.get('assigned_room'))
        patient_entry.assigned_room = assigned_room
        patient_entry.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'], url_path="incomplete")
    def view_incomplete(self, request):
        incomplete_entries = self.get_queryset().filter(completed=False)
        serializer = self.serializer_class(instance=incomplete_entries, many=True)
        return Response(serializer.data)
 
class RoomViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    @action(detail=False, methods=['GET'], url_path=r"floor/(?P<floor_number>[0-9]+)")
    def view_rooms_by_floor(self, request, floor_number):
        rooms_by_floor = self.get_queryset().filter(floor=floor_number)
        serializer = self.serializer_class(instance=rooms_by_floor, many=True)
        return Response(serializer.data)

class PatientViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]  
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class FeedbackViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

## OPTIONAL FEATURE ##
class FeedbackForStaffViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = FeedbackForStaff.objects.all()
    serializer_class = FeedbackForStaffSerializer
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)
    
    @action(detail=False, methods=['GET'], url_path=r'(staff/?P<staff_id>[0-9]+)')
    def view_feedback_by_staff(self, request, staff_id):
        feedback_by_staff = self.get_queryset().filter(staff__id=staff_id)
        serializer = self.serializer_class(istance=feedback_by_staff, many=True)
        return Response(serializer.data)