from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom User
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

# User
class User(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(unique=True)
    username        = models.CharField(max_length=30, unique=True)  # Add username field
    first_name      = models.CharField(max_length=30)
    last_name       = models.CharField(max_length=30)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    ROLE_CHOICES    = (
                    ('Examiner', 'Examiner'),
                    ('Examinee', 'Examinee'),
                    )
    role            = models.CharField(max_length=8, choices=ROLE_CHOICES, default='Examinee')

    objects         = CustomUserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']  # Add 'username' to the REQUIRED_FIELDS

    def __str__(self):
        return self.email
    
class UserProfile(models.Model):
    GENDER_CHOICES      = (('M', 'M'),('F', 'F'),('O','O'))
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    dob                 = models.DateField(max_length=8)
    gender              = models.CharField(max_length=1, choices=GENDER_CHOICES)
    profile_image       = models.ImageField(upload_to='user/profile_images/',blank=True,null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    
# Autorize-Mailer-Domain  Model
class AutorizeMailerDomain(models.Model):
    title                = models.CharField(max_length=100)
    mail_domain_name     = models.CharField(max_length=100)
    created_date         = models.DateTimeField(auto_now_add=True)
    updated_date         = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active            = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Authorize Domain'

# Category Model
class Category(models.Model):
    name               = models.CharField(max_length=255)
    title              = models.CharField(max_length=255)
    is_active          = models.BooleanField(default=True)
    createdDate        = models.DateTimeField(auto_now_add=True)
    modifiedDate       = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return str(self.name)

# Quiz-Creation-Topic Model
class Quiz(models.Model):
    category                          = models.ForeignKey(Category, related_name='quiz_category', on_delete=models.CASCADE)
    name                              = models.CharField(max_length=255)
    title                             = models.CharField(max_length=255)
    total_mark                        = models.IntegerField(default=0, null=True, blank=True)
    no_of_questions                   = models.PositiveBigIntegerField(default=0)
    quiz_time                         = models.TimeField(blank=True,null=True)
    is_active                         = models.BooleanField(default=True)
    createdDate                       = models.DateTimeField(auto_now_add=True)
    modifiedDate                      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

# Quiz-Question Model
class QuizQuestion(models.Model):
    QUIZ_TYPE    =[
        ('text','TEXT'), 
        ('audio','AUDIO'),
        ('video','VIDEO'),
        ('image','IMAGE'),
        ('write','WRITE'),
    ]
    quiz                = models.ForeignKey(Quiz, related_name='quiz_question_quiz', on_delete=models.CASCADE)
    question            = models.TextField(max_length=1000, null=True, blank=True)
    correct_answer      = models.TextField(max_length=1000, null=True, blank=True)
    questions_marks     = models.CharField(max_length=255, null=True, blank=True)
    images              = models.ImageField(upload_to='quiz_question/images/', null=True, blank=True)
    audio_tracks        = models.FileField(upload_to='quiz_question/audio_tracks/',null=True, blank=True)
    video_tracks        = models.FileField(upload_to='quiz_question/video_tracks/',max_length=255, null=True, blank=True)
    quiz_type           = models.CharField(choices=QUIZ_TYPE,max_length=255)
    is_active           = models.BooleanField(default=True)
    createdDate         = models.DateTimeField(auto_now_add=True)
    modifiedDate        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.question)
    
    def save(self, *args, **kwargs):
        super(QuizQuestion, self).save(*args, **kwargs)

        # Calculate the number of questions for the associated quiz
        self.quiz.no_of_questions = self.quiz.quiz_question_quiz.count()
        self.quiz.save()

# Quiz-Options-Creation Model
class QuizOptionsCreator(models.Model):
    quiz_question       = models.ForeignKey(QuizQuestion, related_name="quiz_question_option",on_delete=models.PROTECT)
    option             = models.TextField(max_length=1000, null=True, blank=True)
    correct_flag        = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    createdDate         = models.DateTimeField(auto_now_add=True)
    modifiedDate        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.option)
    
# Quiz-Result Model
class QuizResult(models.Model):
    quiz_id        = models.ForeignKey(Quiz,on_delete=models.PROTECT, related_name='quiz_quiz_result')
    user_id        = models.ForeignKey(User, on_delete=models.PROTECT, related_name='quiz_user_quiz_result')
    quiz_option    = models.ForeignKey(QuizOptionsCreator, on_delete=models.PROTECT, null=True, blank=True, related_name='quiz_user_quiz_result')
    own_answer     = models.TextField(max_length=1000,null=True, blank=True)
    marks_get      = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_attempted   = models.BooleanField(default=False)
    is_ans_correct = models.BooleanField(default=False)
    created_date   = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date   = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.quiz_id)

# Quiz-User Result Model
class QuizUserResult(models.Model):
    quiz_result_id       = models.ForeignKey(QuizResult,on_delete=models.PROTECT, related_name='quiz_quiz_user_rel')
    user_id              = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user_quiz_user_rel')
    total_marks          = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_submit            = models.BooleanField(default=False)
    created_date         = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date         = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.quiz_result_id)


