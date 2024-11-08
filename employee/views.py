from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from django.db.models import Q 
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Employee, EmployeeField
from .serializers import UserRegisterSerializer, EmployeeSerializer, EmployeeFieldSerializer

# User Registration
class RegisterUserView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
         
        if not email or not password:
            return Response({'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate user
        user = get_user_model().objects.filter(email=email).first()
        print(user)
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            is_admin = user.is_staff  # Assuming is_staff denotes admin role
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'name': user.name,  # Directly use `user.name`
                'is_admin': is_admin  # Send the is_admin flag
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)



# Admin Dashboard View (Restricted to Admins only)
class AdminDashboardView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only authenticated admins can access this view


# Employee List View (For all authenticated users)
class EmployeeListView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]  # All authenticated users can access this view


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Only admins can access employee actions

    # @action(detail=False, methods=['post'])  # Action for creating employees
    def create(self, request, *args, **kwargs):
        # Ensure the user is authenticated and has admin permissions
        if not request.user.is_authenticated or not request.user.is_admin:
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Deserialize and validate request data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Save the employee and return the response
            employee = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_queryset(self):
        # Allow searching for employees by name or email
        search_term = self.request.query_params.get('search', '')
        if search_term:
            return self.queryset.filter(
                Q(name__icontains=search_term) | Q(email__icontains=search_term)
            )
        return self.queryset

    def perform_update(self, serializer):
        # Handle updates to employees, including custom fields
        custom_fields = self.request.data.get('custom_fields', [])
        if custom_fields:
            # Optionally, update custom fields if needed
            pass
        serializer.save()



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # The logged-in user is the Employee instance
        employee = request.user
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=200)