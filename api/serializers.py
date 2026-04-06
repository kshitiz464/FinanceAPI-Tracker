from rest_framework import serializers
from .models import User, Transaction
from django.utils import timezone


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for user responses (excludes password)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update user role/status."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']
        read_only_fields = ['id', 'username', 'email']


class TransactionSerializer(serializers.ModelSerializer):
    """Full transaction serializer for read operations."""
    created_by = UserResponseSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating transactions with validation."""
    class Meta:
        model = Transaction
        exclude = ['id', 'created_at', 'updated_at', 'is_deleted', 'created_by']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be a positive number.')
        if value > 999_999_999:
            raise serializers.ValidationError('Amount exceeds maximum allowed value.')
        return value

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError('Transaction date cannot be in the future.')
        return value

    def validate_category(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Category must be at least 2 characters.')
        return value.strip()
