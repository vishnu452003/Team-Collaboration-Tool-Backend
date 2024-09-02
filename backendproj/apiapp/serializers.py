from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
import re
from .models import Workspace, Project

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']
    
    def validate_username(self, value):
        # Regular expression for username validation
        if not re.match(r'^[A-Za-z]\w{7,29}$', value):
            raise serializers.ValidationError(
                "Username must start with an alphabet and can contain alphabets, numbers, or underscores. Length should be 8-30 characters."
            )
        return value
    
    def validate_password(self, value):
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        return {'user': user}

class PasswordResetRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User with this username does not exist.")
        return value



class PasswordResetConfirmSerializer(serializers.Serializer):
    username = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        #validate_password(value)
        return value

    def save(self):
        username = self.validated_data['username']
        new_password = self.validated_data['new_password']

        
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

class WorkspaceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'description', 'owner', 'members', 'created_at', 'updated_at']

class ProjectSerializer(serializers.ModelSerializer):
    workspace = serializers.ReadOnlyField(source='workspace.name')

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'workspace', 'created_at', 'updated_at']
