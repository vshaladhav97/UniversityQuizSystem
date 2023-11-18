# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user_profile/<int:user_id>', UserProfileView.as_view(), name="user_profile"),
    path('category/', QuizCategoryView.as_view(), name="category"),
    path('quiz/<category_id>/', QuiView.as_view(), name="get_quiz"),
    path('quiz/', QuiView.as_view(), name="quiz"),
    path('quizzes/<int:quiz_id>/', QuiView.as_view(), name='quiz-detail'),
    path('quiz_question/<int:quiz_id>/', QuizQuestionsView.as_view(), name="quiz_question")

]