from django.shortcuts import render

from django.contrib.auth import logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import *
from .utils import *
from django.contrib.auth import get_user_model
from rest_framework import permissions, generics,status
User = get_user_model() 

# User Registration View
class UserRegistration(APIView):
    def post(self, request):
        error_message = registervalidations(request.data)
        if error_message:
            return Response({'error': [error_message]}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {   
                    'result': "Your registration has been done successfully!",
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login view
class UserLogin(APIView):
    def post(self, request):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if username_or_email and password:
                # Attempt to authenticate using username
                user = authenticate(request, username=username_or_email, password=password)
                if user is None:
                    # Attempt to authenticate using email
                    try:
                        user = User.objects.get(email=username_or_email)
                        user = authenticate(request, username=user.username, password=password)
                    except User.DoesNotExist:
                        user = None
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {   
                            'result': "User Login Successfully",
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)
                        },
                        status=status.HTTP_200_OK
                    )
        # If no valid user was found or the input is invalid, return an error response
        return Response({'result': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
# Logout class
class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh_token']
            try:
                RefreshToken(refresh_token).blacklist()
                logout(request)
                return Response({'detail': 'Logout successful'}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({'detail': 'Unable to logout'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, user_id):
        user_data = User.objects.get(id = user_id)
        if user_data:
            first_name = user_data.first_name
            last_name = user_data.last_name
            username = user_data.username
            email = user_data.email
            role = user_data.role
            return Response({
                "first_name" : first_name,
                "last_name" : last_name,
                "username" : username ,
                "email" : email,
                "role" : role
             }, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "Invalid Request or User Doesn't Exists"}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request, user_id):
        user_data = User.objects.get(id=user_id)
        print(user_data)
        if user_data:
            serializer = UserProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "Invalid Request or User Doesn't Exist"}, status=status.HTTP_400_BAD_REQUEST)
        

class QuizCategoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        try:
            category_data = Category.objects.filter(is_active=True)
            serializer = CategorySerializer(category_data, many=True)

            if category_data:
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"data": []}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = request.data
        if not data:
            return Response({'error': "Missing Payload!"}, status=204)
        try:
            check_category = Category.objects.filter(name = data['name'])
            if check_category:
                return Response({'error': f"Category Name : {data['name']} already exists!"}, status=409)
            
            category = Category()
            if data['name'] == "" or data['name'] == None or data['name'] == type(int):
                return Response({'error': "Catogory name cannot have the following : Empty string, Null and Integer value!"}, status=400)
            else:
                category.name = data['name']
            if data['title'] == "" or data['title'] == None or data['title'] == type(int):
                return Response({'error': "Catogory title cannot have the following : Empty string, Null and Integer value!"}, status=400)
            else:
                category.title = data['title']
            category.save()
            return Response({'id': category.id, 'message': 'Category created successfully'}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

