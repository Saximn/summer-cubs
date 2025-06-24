
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from rest_framework import viewsets, permissions
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
  
class PatientEntryView(APIView):
    def get(self, request):
        patient_entries = PatientEntry.objects.all()
        serializer = PatientEntrySerializer(patient_entries)