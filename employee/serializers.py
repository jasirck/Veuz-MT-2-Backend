from rest_framework import serializers
from .models import Employee, EmployeeField

from rest_framework import serializers
from .models import Employee, EmployeeField

class EmployeeFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeField
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    custom_fields = EmployeeFieldSerializer(many=True, required=False)

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        employee = Employee.objects.create(**validated_data)
        for field_data in custom_fields_data:
            EmployeeField.objects.create(employee=employee, **field_data)
        return employee

    def update(self, instance, validated_data):
        custom_fields_data = validated_data.pop('custom_fields', [])
        instance = super().update(instance, validated_data)

        # Update custom fields logic (optional)
        if custom_fields_data:
            instance.custom_fields.all().delete()  # Delete existing custom fields (if necessary)
            for field_data in custom_fields_data:
                EmployeeField.objects.create(employee=instance, **field_data)

        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [ 'email', 'password', 'name', 'position', 'is_admin']

    def create(self, validated_data):
        user = Employee.objects.create_user(**validated_data)
        return user


