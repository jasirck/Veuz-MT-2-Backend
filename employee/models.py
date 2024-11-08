from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Custom manager for Employee model
class EmployeeManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)

# Employee model using AbstractBaseUser
class Employee(AbstractBaseUser):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = EmployeeManager()

    def __str__(self):
        return self.name or self.email

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_active(self):
        return True

# EmployeeField model for custom fields
class EmployeeField(models.Model):
    employee = models.ForeignKey(Employee, related_name='custom_fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=50)
    field_type = models.CharField(max_length=50)
    field_value = models.TextField()

    def __str__(self):
        return f"{self.field_name}: {self.field_value}"
