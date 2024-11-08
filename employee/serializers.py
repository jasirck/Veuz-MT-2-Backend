from rest_framework import serializers
from .models import Employee, EmployeeField


class EmployeeFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeField
        fields = '__all__'

# Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    custom_fields = EmployeeFieldSerializer(many=True, required=False)
    password = serializers.CharField(write_only=True, required=False)  # Password field

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'position', 'is_admin', 'custom_fields', 'password']  # Add password field

    def create(self, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        password = validated_data.pop('password', None)

        # If password is provided, hash it and set it on the employee
        if password:
            employee = Employee.objects.create_user(**validated_data)  # Create employee with hashed password
        else:
            employee = Employee.objects.create(**validated_data)

        # Create custom fields if provided
        for field_data in custom_fields_data:
            EmployeeField.objects.create(employee=employee, **field_data)

        return employee

    def update(self, instance, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        password = validated_data.pop('password', None)

        # If password is provided, hash it and update it
        if password:
            instance.set_password(password)
        
        instance = super().update(instance, validated_data)

        # Update custom fields logic (optional)
        if custom_fields_data:
            instance.custom_fields.all().delete()  # Delete existing custom fields (if necessary)
            for field_data in custom_fields_data:
                EmployeeField.objects.update(employee=instance, **field_data)

        return instance

# User Register Serializer
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['email', 'password', 'name', 'position', 'is_admin']

    def create(self, validated_data):
        user = Employee.objects.create_user(**validated_data)
        return user
