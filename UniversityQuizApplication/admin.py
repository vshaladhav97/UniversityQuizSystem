from django.contrib import admin
from .models import *
# Register your models here.

# User Admin Fields List
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'role',]

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "dob", "gender"]

# User Authorize Domain Fields List
class AuthorizeMailerDomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'mail_domain_name', 'created_date', 'updated_date', 'is_active',]

# Create admin classes for your models
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'is_active', 'createdDate', 'modifiedDate')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'title', 'category', 'total_mark', 'no_of_questions', 'quiz_time', 'is_active', 'createdDate', 'modifiedDate')

class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('id','question', 'quiz', 'quiz_type', 'is_active', 'createdDate', 'modifiedDate')

class QuizOptionsCreatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_id', 'quiz_question','quiz_question_id', 'option', 'correct_flag', 'is_active', 'createdDate', 'modifiedDate')

    def quiz_id(self, obj):
        # Access the quiz_id using the double-underscore notation
        return obj.quiz_question.quiz_id

    quiz_id.short_description = 'Quiz ID'

class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_id', 'user_id', 'own_answer','question_id', 'marks_get', 'question_marks', 'is_attempted', 'is_ans_correct', )

class QuizUserResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz_result_id', 'user_id', 'total_marks', 'is_submit')


# Registering all the tables
admin.site.register(User, UserAdmin)
admin.site.register(AutorizeMailerDomain, AuthorizeMailerDomainAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizOptionsCreator, QuizOptionsCreatorAdmin)
admin.site.register(QuizResult, QuizResultAdmin)
admin.site.register(QuizUserResult, QuizUserResultAdmin)
admin.site.register(UserProfile, UserProfileAdmin)