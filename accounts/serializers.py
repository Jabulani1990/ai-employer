from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Skill

User = get_user_model()

# Skill Serializer
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)  # Display skills in profile

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "account_type", "skills"]

# Registration Serializer (No skills during registration)
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "account_type", "first_name", "last_name"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            account_type=validated_data["account_type"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        
        user = authenticate(username=data["username"], password=data["password"])
        if user is None:
            raise serializers.ValidationError("Invalid credentials")
        
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data
        }

# Assign Skills to User
class AssignSkillsSerializer(serializers.Serializer):
    skill_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    def update(self, instance, validated_data):
        skill_ids = validated_data.get("skill_ids", [])
        instance.skills.set(Skill.objects.filter(id__in=skill_ids))
        return instance
