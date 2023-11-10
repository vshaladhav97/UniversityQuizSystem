# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistration.as_view(), name='user-registration'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user_profile/<int:user_id>', UserProfileView.as_view(), name="user_profile"),
    path('category/', QuizCategoryView.as_view(), name="category")
    # Add more URL patterns for login, profile, etc.
]