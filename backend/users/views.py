
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response


from .serializers import *
from .models import *

User = get_user_model()

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = RegisterSerializer(request.user)
        return Response(serializer.data)

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
                    "user": UserSerializer(user).data,
                    "token": token,

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
        print(serializer.errors)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['POST'], url_path="assign_room")
    def assign_room(self, request, pk=None):
        patient_entry = self.get_object()
        room_data = request.data.get("assigned_room")

        if not room_data or not room_data.get("room_number") or not room_data.get("floor"):
            return Response({"error": "Missing 'room_number' or 'floor'"}, status=400)

        try:
            assigned_room = Room.objects.get(room_number=room_data["room_number"], floor=room_data["floor"])
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)
        except Room.MultipleObjectsReturned:
            return Response({"error": "Multiple rooms found; floor must be specified uniquely"}, status=400)

        patient_entry.assigned_room = assigned_room
        patient_entry.save()

        serializer = self.serializer_class(patient_entry)
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

    @action(detail=False, methods=['GET'], url_path='availability')
    def availability_per_floor(self, request):
        availability = {}

        for floor in range(1, 6):  # floors 1 to 5
            floor_rooms = Room.objects.filter(floor=floor)
            available_count = 0

            for room in floor_rooms:
                occupied = PatientEntry.objects.filter(assigned_room=room, completed=False).count()
                if occupied < room.capacity:
                    available_count += 1

            availability[floor] = available_count

        return Response(availability)

class PatientViewset(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    permission_classes = [permissions.IsAuthenticated]  
    quertset = Patient.objects.all()
    serializer_class = PatientSerializer