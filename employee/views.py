from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.db.models import Q 
from .models import Employee, EmployeeField
from .serializers import UserRegisterSerializer, EmployeeSerializer, EmployeeFieldSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets


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
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            is_admin = user.is_staff  # Assuming is_staff denotes admin role
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'name': user.name,
                'is_admin': is_admin
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

# Admin Dashboard View (Restricted to Admins only)
class AdminDashboardView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        print(request.user.email)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        search_term = self.request.query_params.get('search', '')
        if search_term:
            return self.queryset.filter(
                Q(name__icontains=search_term) | Q(email__icontains=search_term)
            )
        return self.queryset
    def update(self, request, *args, **kwargs):
        employee = self.get_object()

        # Ensure the employee can only update their own data
        if employee != request.user:
            return Response({'detail': 'You do not have permission to update this employee.'}, status=403)

        return super().update(request, *args, **kwargs)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        serializer = EmployeeSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = EmployeeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
