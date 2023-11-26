from rest_framework import serializers
from .models import *
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.exceptions import TokenError


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



# For Examiner
class QuizOptionsCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOptionsCreator
        fields = '__all__'

# For Examiner
class QuizQuestionSerializer(serializers.ModelSerializer):
    quiz_question_option = QuizOptionsCreatorSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = '__all__'

# For Examiner
class QuizSerializer(serializers.ModelSerializer):
    quiz_question_quiz = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

# For Student
class QuizOptionsCreatorStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOptionsCreator
        fields = ['id', 'quiz_question', 'option'] 

# For Student
class QuizQuestionStudentSerializer(serializers.ModelSerializer):
    quiz_question_option = QuizOptionsCreatorStudentSerializer(many=True, read_only=True)

    class Meta:
        model = QuizQuestion
        fields = '__all__'

# For Student
class QuizStudentSerializer(serializers.ModelSerializer):
    quiz_question_quiz = QuizQuestionStudentSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = '__all__'

