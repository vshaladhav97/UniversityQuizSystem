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
    path('quiz_question/<int:quest_id>/', QuizQuestionsView.as_view(), name="quiz_question"),
    path('quiz_question/', QuizQuestionsView.as_view(), name="quiz_question"),
    path('quiz_all_data/<int:quiz_id>/', QuizAllDataView.as_view(), name="quiz_options"),
    path('quiz_with_options_for_student/<int:quiz_id>/', StudentQuizDataView.as_view(), name="quiz_with_options_for_student"),
    path('quiz_submit/', StudentQuizDataView.as_view(), name="quiz_submit"),
    path('quiz_statistics/<int:quiz_id>/', QuizStatisticsView.as_view(), name="quiz_statistics"),
    path('quiz_data/<int:category_id>/', QuizDataView.as_view(), name="quiz_data"),
    path('quiz_users_data/<int:quiz_id>/', CurrentUserResultView.as_view(), name="quiz_users_data"),
    path('quiz_question_update/', QuizQuestionUpdateView.as_view(), name="quiz_question_update")

]