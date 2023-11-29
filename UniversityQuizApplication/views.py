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
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Avg, Max, Min

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
                            'refresh': str(refresh),
                            'is_examinee': True if user.role == "Examinee" else False
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
                return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
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
                return Response({"data": []}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        data = request.data
        if not data:
            return Response({'error': "Missing Payload!"}, status=200)
        try:
            check_category = Category.objects.filter(name = data['name'])
            if check_category:
                return Response({'error': f"Category Name : {data['name']} already exists!"}, status=409)
            
            category        = Category()
            category.user   = User.objects.get(id=request.user.id)
            if data['name'] == "" or data['name'] == None or data['name'] == type(int):
                return Response({'error': "Catogory name cannot have the following : Empty string, Null and Integer value!"}, status=400)
            else:
                category.name = data['name']
            if data['title'] == "" or data['title'] == None or data['title'] == type(int):
                return Response({'error': "Catogory title cannot have the following : Empty string, Null and Integer value!"}, status=400)
            else:
                category.title = data['title']
            category.save()
            data = {
                "category_id": category.id,
                "message" : 'Category created successfully',
            }
            return Response({'data': data}, status=201)
        except Exception as e:
            data = {
                "message" : str(e),
            }
            return Response({'data': data}, status=400)


class QuiView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request, category_id):
        try:
            quiz_data = Quiz.objects.filter(category = category_id,is_active=True)
            serializer = QuizSerializer(quiz_data, many=True)
            if quiz_data:
                data = {'data': serializer.data, 'message': 'Categories fetched successfully!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                data = {'data': [], 'message': 'Data not found!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            data = {'data': [], 'message': 'str(e)'}
            return Response({'data': data}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        data = request.data
        if not data:
            data = {'data': [], 'message': 'Data not found!'}
            return Response({'data':data}, status=200)
        try:
            check_quiz = Quiz.objects.filter(name = data['name'], category_id = data['category_id'])
            if check_quiz:
                data = {'data': [], 'message': f"Quiz Name : {data['name']} already exists!"}
                return Response({'data': data}, status=409)
            
            quiz        = Quiz()
            quiz.category = Category.objects.get(id = data['category_id'])
            if data['name'] == "" or data['name'] == None or data['name'] == type(int):
                data = {'data': [], 'message': "Quiz name cannot have the following : Empty string, Null and Integer value!"}
                return Response({'data': data}, status=400)
            else:
                quiz.name = data['name']
            if data['title'] == "" or data['title'] == None or data['title'] == type(int):
                data = {'data': [], 'message': "Quiz title cannot have the following : Empty string, Null and Integer value!"}
                return Response({'data': data}, status=400)
            else:
                quiz.title = data['title']
            if data['total_mark'] == "" or data['total_mark'] == None or data['total_mark'] == type(str):
                data = {'data': [], 'message': "Quiz total_mark cannot have the following : Empty string, Null and String value!"}
                return Response({'data': data}, status=400)
            else:
                quiz.total_mark = data['total_mark']
            if data['quiz_time'] == "" or data['quiz_time'] == None or data['quiz_time'] == type(str):
                data = {'data': [], 'message': "Quiz quiz_time cannot have the following : Empty string, Null and String value!"}
                return Response({'data': data}, status=400)
            else:
                quiz.quiz_time = data['quiz_time']
            quiz.save()
            data = {'data': [], 'message': 'Quiz created successfully'}
            return Response({'data': data}, status=201)
        except Exception as e:
            data = {'data': [], 'message': 'str(e)'}
            return Response({'data': data}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, quiz_id):
        print(quiz_id)
        data = request.data
        if not data:
            data = {'data': [], 'message': "Missing Payload!"}
            return Response({'data': data}, status=status.HTTP_200_OK)
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            # Update the quiz fields if provided in the request data
            if 'category_id' in data:
                quiz.category = Category.objects.get(id = data['category_id'])

            if 'name' in data:
                quiz.name = data['name']

            if 'title' in data:
                quiz.title = data['title']

            if 'total_mark' in data:
                quiz.total_mark = data['total_mark']

            if 'quiz_time' in data:
                quiz.quiz_time = data['quiz_time']

            quiz.save()
            data = {'data': [], 'message': 'Quiz updated successfully'}
            return Response({'data': data}, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            data = {'data': [], 'message': 'Quiz not found'}
            return Response({'data': data}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({'data': data}, status=status.HTTP_400_BAD_REQUEST)

class QuizQuestionsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request, quest_id):
        try:
            quiz_questions = QuizQuestion.objects.filter(id=quest_id,is_active=True)
            serializer = QuizQuestionSerializer(quiz_questions, many=True)
            if quiz_questions:
                data = {'data': serializer.data, 'message': 'Quiz Fetched Successfully!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                data = {'data': [], 'message': 'Quiz Not Found!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({'data':data}, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def post(self, request):
        data = request.data
        if not data:
            data = {'data': [], 'message': "Missing Payload!"}
            return Response({'data': data}, status=status.HTTP_200_OK)
        
        try:
            check_quiz = Quiz.objects.filter(id=data['quiz_id'])
            if not check_quiz:
                data = {'data': [], 'message': f"Quiz id : {data['quiz_id']} does not exist in the Database!"}
                return Response({'data': data}, status=409)

            quiz_question = QuizQuestion()
            quiz_question.quiz = check_quiz.first()

            if not data['question']:
                data = {'data': [], 'message': "Question cannot be empty!"}
                return Response({'data': data}, status=400)
            else:
                quiz_question.question = data['question']

            if not isinstance(data['questions_marks'], int):
                data = {'data': [], 'message': "Question marks must be an integer!"}
                return Response({'data': data}, status=400)
            else:
                quiz_question.questions_marks = data['questions_marks']

            if not data['quiz_type']:
                data = {'data': [], 'message': "Quiz type cannot be empty!"}
                return Response({'data': data}, status=400)
            else:
                quiz_question.quiz_type = data['quiz_type']

            quiz_question.save()

            # Options data code
            options_data = data.get('options', [])
            
            for i in options_data:
                quiz_option                 = QuizOptionsCreator()
                quiz_option.quiz_question   = quiz_question
                quiz_option.option          = i['option']
                quiz_option.correct_flag    = i['correct_flag']
                quiz_option.save() 

             # Return a success response
            data = {'data': [{'id':  f"Question id : {quiz_question.id} Quiz Questions created successfully!"}], 'message': 'Quiz Questions created successfully'}
            return Response({'data': data}, status=status.HTTP_201_CREATED) 

        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({'data': data}, status=400)

class QuizAllDataView(APIView):

    def get(self,request, quiz_id):
        try:
            quiz_questions = Quiz.objects.filter(id=quiz_id,is_active=True)
            serializer = QuizSerializer(quiz_questions, many=True)
            if quiz_questions:
                data = {'data': serializer.data, 'message': 'Quiz Fetched Successfully!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                data = {'data': [], 'message': 'Quiz Not Found!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({'data':data}, status=status.HTTP_400_BAD_REQUEST)
    
class StudentQuizDataView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self,request, quiz_id):
        try:
            quiz_questions = Quiz.objects.filter(id=quiz_id,is_active=True)
            serializer = QuizStudentSerializer(quiz_questions, many=True)
            if quiz_questions:
                data = {'data': serializer.data, 'message': 'Quiz Fetched Successfully!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
            else:
                data = {'data': [], 'message': 'Quiz Not Found!'}
                return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({'data':data}, status=status.HTTP_400_BAD_REQUEST)
    
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                jason_data = request.data
                quiz_id = jason_data['quiz_id']
                user_id = request.user.id
                auto_submit = jason_data['auto_submit']
                
                user_submitted = QuizUserResult.objects.filter(quiz_result_id = quiz_id, user_id = user_id)
                if user_submitted:
                    data = {'data': [], 'message': 'User has already submitted this quiz!'}
                    return Response({"data": data}, status=status.HTTP_200_OK) 
                if not len(jason_data['questions'])>0:
                    data = {'data': [], 'message': 'user should submit some questions!'}
                    return Response({"data": data}, status=status.HTTP_200_OK) 
                
                for data in jason_data['questions']:
                    question_id = data['question_id']
                    if data['type'] == "multi_choice":
                        if data['option_id']:
                            try:
                                quiz_question = QuizOptionsCreator.objects.get(id=data['option_id'], quiz_question=data['question_id'])
                            except ObjectDoesNotExist:
                                # Handle the case where the object is not found
                                error_message = f"Object with option id: ={data['option_id']} and question id: ={data['question_id']} does not exist."
                                data = {'data': [], 'message': error_message}
                                return Response({"data": data}, status=status.HTTP_200_OK)
                        
                            question_marks      = quiz_question.quiz_question.questions_marks
                            option_correct_flag = quiz_question.correct_flag
                            user_get_marks      = question_marks if option_correct_flag is True else 0
                        else:
                            try:
                                quiz_question = QuizQuestion.objects.get(id=data['question_id'])
                            except ObjectDoesNotExist:
                                # Handle the case where the object is not found
                                error_message = f"Object with option id: ={data['option_id']} and question id: ={data['question_id']} does not exist."
                                data = {'data': [], 'message': error_message}
                                return Response({"data": data}, status=status.HTTP_200_OK)
                            question_marks      = quiz_question.questions_marks
                            user_get_marks = 0 

                    elif data['type'] == "multi_select":
                        if data['option_id']:
                            correct_options_count = QuizOptionsCreator.objects.filter(quiz_question_id=data['question_id'], correct_flag=True).count()
                            print(correct_options_count, "correct_count")
                            correct_op_count = 0
                            for op_id in data['option_id']:
                                try:
                                    quiz_question = QuizOptionsCreator.objects.get(id=op_id, quiz_question=data['question_id'])
                                except ObjectDoesNotExist:
                                    # Handle the case where the object is not found
                                    error_message = f"Object with option id: ={data['option_id']} and question id: ={data['question_id']} does not exist."
                                    data = {'data': [], 'message': error_message}
                                    return Response({"data": data}, status=status.HTTP_200_OK)
                                
                                option_correct_flag = quiz_question.correct_flag
                                correct_op_count += 1 if option_correct_flag is True else 0
                                        
                            question_marks      = quiz_question.quiz_question.questions_marks 
                            if correct_options_count != 0:
                                calculate_marks = correct_op_count / correct_options_count * int(question_marks)
                                user_get_marks = calculate_marks if calculate_marks else 0
                            else:
                                user_get_marks = 0 
                        else:
                            try:
                                quiz_question = QuizQuestion.objects.get(id=data['question_id'])
                            except ObjectDoesNotExist:
                                # Handle the case where the object is not found
                                error_message = f"Object with option id: ={data['option_id']} and question id: ={data['question_id']} does not exist."
                                data = {'data': [], 'message': error_message}
                                return Response({"data": data}, status=status.HTTP_200_OK)
                            question_marks      = quiz_question.questions_marks
                            user_get_marks = 0 

            

                    quiz_result                 = QuizResult()
                    quiz_result.quiz_id         = Quiz.objects.get(id = quiz_id)
                    quiz_result.user_id         = User.objects.get(id = user_id)
                    quiz_result.question_id     = QuizQuestion.objects.get(id = question_id)
                    # quiz_result.quiz_option     = QuizOptionsCreator.objects.get(id = data['option_id'])
                    quiz_result.own_answer      = ""
                    if data['type'] == "multi_select":
                        if len(data['option_id']) > 0:
                            quiz_result.marks_get = user_get_marks if user_get_marks else 0
                        else:
                            quiz_result.marks_get = 0
        
                    elif data['type'] == "multi_choice":
                        if data['option_id']:
                            quiz_result.marks_get       = user_get_marks if user_get_marks else 0
                        else:
                            quiz_result.marks_get       = 0
                    quiz_result.question_marks  = question_marks if question_marks else 0
                    quiz_result.is_attempted    = data['is_attempted']
                    try:
                        quiz_result.is_ans_correct  = True if option_correct_flag is True else False
                    except:
                        quiz_result.is_ans_correct = False
                    quiz_result.save()
                    option_ids = data['option_id']

                    if data['type'] == "multi_select":
                        if len(data['option_id']) > 0:
                            quiz_options_queryset = QuizOptionsCreator.objects.filter(id__in=option_ids)
                            quiz_result.quiz_option.set(quiz_options_queryset)
                        
                    else:
                        if data['option_id']:
                            quiz_options_queryset = QuizOptionsCreator.objects.filter(id=option_ids)
                            quiz_result.quiz_option.set(quiz_options_queryset)


                    # if len(data['option_id']) > 0 or data['option_id']:
                    #     # Assign the queryset to the quiz_options field
                    #     quiz_result.quiz_option.set(quiz_options_queryset)

                    # Save the related models
                    quiz_result.quiz_id.save()
                    quiz_result.user_id.save()
                    quiz_result.question_id.save()

                check_total_marks_user_get        = QuizResult.objects.filter(user_id=user_id, quiz_id=quiz_id).aggregate(Sum('marks_get'))['marks_get__sum']
                total_questions_marks             = QuizResult.objects.filter(user_id=user_id, quiz_id=quiz_id).aggregate(Sum('question_marks'))['question_marks__sum']
                print(check_total_marks_user_get / total_questions_marks)
                total_marks_user_get        = check_total_marks_user_get / total_questions_marks * 100 if total_questions_marks > 0 else 0
                
                user_result                 = QuizUserResult()
                user_result.quiz_result_id  = Quiz.objects.get(id = quiz_id)
                user_result.user_id         = User.objects.get(id = user_id)
                user_result.total_marks     = total_marks_user_get
                user_result.is_submit       = auto_submit
                user_result.save()

                # other users data
                # Order QuizUserResult data by total_marks in descending order
                quiz_user_results = QuizUserResult.objects.filter(quiz_result_id=quiz_id).order_by('-total_marks')

                # Get the requested user's data
                requested_user_data = quiz_user_results.filter(user_id=request.user.id).first()

                # Serialize the data
                serializer = QuizUserResultSerializer(quiz_user_results, many=True)

                # If requested user's data is present, show it first; otherwise, display all data
                if requested_user_data:
                    result_data = [QuizUserResultSerializer(requested_user_data).data] + serializer.data
                else:
                    result_data = serializer.data

                data = {'data': [{"user_id":user_id, "marks_get":  total_marks_user_get, "total_questions": total_questions_marks}], 'quiz_users_data': result_data, 'message': 'Quiz Submitted Successfully!'}
                return Response({"data": data}, status=status.HTTP_200_OK) 
        except Exception as e:
            data = {'data': [], 'message': str(e)}
            return Response({"data": data}, status=status.HTTP_400_BAD_REQUEST) 


class QuizDataView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, category_id):
        quizzes = Quiz.objects.filter(category = category_id)

        # Serialize the quizzes using the serializer
        serializer = OnlyQuizSerializer(quizzes, many=True)

        # Return the serialized data in the response
        data = {'data': serializer.data, 'message': 'Quizzes fetched successfully'}
        return Response(data, status=status.HTTP_200_OK)

class QuizStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, quiz_id):

        # import matplotlib.pyplot as plt

        # Pie chart data

        # Get the queryset of QuizUserResult
        queryset = QuizUserResult.objects.filter(quiz_result_id=quiz_id)

        # Serialize the queryset using the serializer
        serializer = QuizUserResultSerializer(queryset, many=True)

        # Retrieve the serialized data
        serialized_data = serializer.data

        # Calculate average marks
        average_marks = queryset.aggregate(Avg('total_marks'))['total_marks__avg']

        # Get top 5 scores
        top_5_scores = queryset.order_by('-total_marks')[:5]

        # Get bottom 5 scores
        bottom_5_scores = queryset.order_by('total_marks')[:5]

        # Lowest Score
        lowest_score = queryset.aggregate(Min('total_marks'))['total_marks__min']

        # Highest Score
        highest_score = queryset.aggregate(Max('total_marks'))['total_marks__max']

        labels = ['Lowest Score', 'Average Score', 'Highest Score']
        sizes = [lowest_score, average_marks, highest_score]
        explode = (0.1, 0, 0)  # explode the slice with the lowest score
        colors = ['#ff9999', '#66b3ff', '#99ff99']

        # # Create the pie chart
        # fig, ax = plt.subplots()
        # ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
        #     shadow=True, startangle=90)
        # ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        # plt.title('Distribution of Scores')
        # plt.show()


        # categories = ['Lowest Score', 'Average Score', 'Highest Score']
        # scores = [lowest_score, average_marks, highest_score]

        # # Create the bar chart
        # plt.bar(categories, scores, color=['red', 'blue', 'green'])
        # plt.xlabel('Categories')
        # plt.ylabel('Scores')
        # plt.title('Distribution of Scores')
        # plt.show()

        context = {
            'average_marks': average_marks,
            'lowest_marks': lowest_score,
            'highest_score': highest_score,
            'top_5_scores': QuizUserResultSerializer(top_5_scores, many=True).data,
            'bottom_5_scores': QuizUserResultSerializer(bottom_5_scores, many=True).data,
        }

        data = {'data': context, 'message': 'Quiz Statistics fetched properly'}
        return Response({"data": data}, status=status.HTTP_200_OK) 



class CurrentUserResultView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, quiz_id):
        try:
            # Order QuizUserResult data by total_marks in descending order
            quiz_user_results = QuizUserResult.objects.filter(quiz_result_id=quiz_id).order_by('-total_marks')

            # Get the requested user's data
            requested_user_data = quiz_user_results.filter(user_id=request.user.id).first()

            # Serialize the data
            serializer = QuizUserResultSerializer(quiz_user_results, many=True)

            # If requested user's data is present, show it first; otherwise, display all data
            if requested_user_data:
                result_data = [QuizUserResultSerializer(requested_user_data).data] + serializer.data
            else:
                result_data = serializer.data

            return Response(result_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
