# from rest_framework import serializers
# from .models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'password', 'first_name', 'last_name']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         user = User.objects.create(
#             email=validated_data['email'],
#             first_name=validated_data['first_name'],
#             last_name=validated_data['last_name']
#         )
#         user.set_password(validated_data['password'])  # Hash the password
#         user.save()
#         return user


from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'role']  # Include 'username'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],  # Include 'username'
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role = validated_data['role']
        )
        user.set_password(validated_data['password']) 
        user.save()
        return user
    

# Logout Serializer
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'