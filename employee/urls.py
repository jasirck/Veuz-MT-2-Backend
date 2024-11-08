from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, RegisterUserView, LoginView, AdminDashboardView, ProfileView

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('profile/', ProfileView.as_view(), name='profile'),  # New profile endpoint
]

# Add the router URLs for the `EmployeeViewSet`
urlpatterns += router.urls
