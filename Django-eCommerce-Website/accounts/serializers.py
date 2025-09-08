# C:\Users\archi\Downloads\Folder2\Django-eCommerce-Website\accounts\serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model (for displaying user details).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a user's profile, including their first/last name,
    phone number, and address.
    """
    phone_number = serializers.CharField(source='profile.phone_number', required=False, allow_blank=True)
    address = serializers.CharField(source='profile.address', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'address')

    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        # Update or create the related Profile instance
        profile_data = validated_data.pop('profile', {})
        profile_instance, created = Profile.objects.get_or_create(user=instance)

        profile_instance.phone_number = profile_data.get('phone_number', profile_instance.phone_number)
        profile_instance.address = profile_data.get('address', profile_instance.address)
        profile_instance.save()
        
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password creation and validation.
    """
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {'username': {'required': False}}

    def validate(self, data):
        # Ensure passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        # Validate password strength
        try:
            validate_password(data['password'], user=User(**data))
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # Ensure email is unique
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        username = validated_data.get('username')
        if not username:
            username = validated_data['email']
            
        user = User.objects.create_user(
            email=validated_data['email'],
            username=username,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Uses email and password for authentication.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")
        
        return data
