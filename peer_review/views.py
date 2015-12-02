import datetime
import csv

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.http import JsonResponse
import random
import string

from django.utils import timezone

from .models import Document
from .models import Question, QuestionType, QuestionGrouping, Choice, Rank,Questionnaire, RoundDetail, TeamDetail
from .models import User, UserDetail
from .models import Questionnaire, QuestionOrder
from .forms import DocumentForm, UserForm


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def index(request):
    users = User.objects.all
    userForm = UserForm()
    docForm = DocumentForm()
    return render(request, 'peer_review/userAdmin.html', {'users': users, 'userForm': userForm, 'docForm': docForm})


def fileUpload(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect('')
    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'peer_review/fileUpload.html',
        {'documents': documents, 'form': form}
        , context_instance=RequestContext(request)
    )

def maintainRound(request):
    context = {'roundDetail': RoundDetail.objects.all(),
                'questionnaires': Questionnaire.objects.all()}
    return render(request, 'peer_review/maintainRound.html',context)


def maintainTeam(request):
    context = {'users': User.objects.all(),
                'rounds': RoundDetail.objects.all(),
                'teams': TeamDetail.objects.all()}
    return render(request, 'peer_review/maintainTeam.html', context)


def questionAdmin(request):
    context = {'questionTypes': QuestionType.objects.all(), 'questions': Question.objects.all()}
    return render(request, 'peer_review/questionAdmin.html', context)

def questionnaireAdmin(request):
    context = {'rounds': RoundDetail.objects.all(),
               'questions': Question.objects.all()}
    return render(request, 'peer_review/questionnaireAdmin.html', context)

def questionnaire(request):
	context = {'questionnaire': Questionnaire.objects.all(), 'questions' : Question.objects.all(),
		    'questionTypes' : QuestionType.objects.all(), 'questionOrder' : QuestionOrder.objects.all(),
		    'questionGrouping' : QuestionGrouping.objects.all()}
	return render(request, 'peer_review/questionnaire.html', context)

def userList(request):
    users = User.objects.all
    userForm = UserForm()
    docForm = DocumentForm()
    generateOTP()
    return render(request, 'peer_review/userAdmin.html', {'users': users, 'userForm': userForm, 'docForm': docForm})

def getTeamsForRound(request, roundPk):
    teams = TeamDetail.objects.filter(roundDetail_id=roundPk)
    response = {}
    for team in teams:
        response[team.pk] = {
            'userId': team.userDetail.pk,
            'teamNumber': team.teamNumber,
            'status': team.status
            }
    # print(response)
    return JsonResponse(response)

def generateOTP():
    N = random.randint(4, 10)
    OTP = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                  for _ in range(N))
    return OTP


def submitForm(request):
    if request.method == "POST":
        userForm = UserForm(request.POST)
        if userForm.is_valid():
            post_title = userForm.cleaned_data['title']
            post_initials = userForm.cleaned_data['initials']
            post_name = userForm.cleaned_data['name']
            post_surname = userForm.cleaned_data['surname']
            post_cell = userForm.cleaned_data['cell']
            post_email = userForm.cleaned_data['email']

            userDetail = UserDetail(title=post_title, initials=post_initials, name=post_name, surname=post_surname,
                                    cell=post_cell, email=post_email)
            userDetail.save()

            post_userId = userForm.cleaned_data['userId']
            post_password = userForm.cleaned_data['password']
            post_status = userForm.cleaned_data['status']

            user = User(userId=post_userId, password=post_password, status=post_status, userDetail=userDetail)
            user.save()

            return HttpResponseRedirect("../")
    else:
        userForm = UserForm()
    return HttpResponseRedirect("../")


def userDelete(request, userPk):
    user = User.objects.get(pk=userPk)
    userDetail = user.userDetail

    userDetail.delete()
    user.delete()
    return HttpResponseRedirect('../')


def userUpdate(request, userPk):
    if request.method == "POST":
        user = User.objects.get(pk=userPk)
        userDetail = user.userDetail

        post_userId = request.POST.get("userId")
        post_title = request.POST.get("title")
        post_initials = request.POST.get("initials")
        post_name = request.POST.get("name")
        post_surname = request.POST.get("surname")
        post_cell = request.POST.get("cell")
        post_email = request.POST.get("email")

        user.userId = post_userId
        userDetail.title = post_title
        userDetail.initials = post_initials
        userDetail.name = post_name
        userDetail.surname = post_surname
        userDetail.cell = post_cell
        userDetail.email = post_email

        user.save()
        userDetail.save()
    return HttpResponseRedirect('../')


def submitCSV(request):
    global errortype
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            filePath = newdoc.docfile.url
            filePath = filePath[1:]

            documents = Document.objects.all()

            # ToDo possibly delete older files

            count = 0
            with open(filePath) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    count += 1
                    if validate(row) == 1:
                        title = row['title']
                        initials = row['initials']
                        name = row['name']
                        surname = row['surname']
                        email = row['email']
                        cell = row['cell']

                        userDetail = UserDetail(title=title, initials=initials, name=name, surname=surname, cell=cell,
                                                email=email)
                        userDetail.save()

                        userId = row['user_id']
                        status = row['status']
                        password = row['password']

                        user = User(userId=userId, password=password, status=status, userDetail=userDetail)
                        user.save()
                        # ToDo check for errors in multiple rows
                    else:
                        if validate(row) == 0:
                            message = "Oops! Something seems to be wrong with the CSV file."
                            errortype = "Incorrect number of fields."
                            return render(request, 'peer_review/csvError.html',
                                          {'message': message, 'error': errortype})
                        else:
                            message = "Oops! Something seems to be wrong with the CSV file at row " + str(count) + "."

                            rowlist = list()
                            rowlist.append(row['title'])
                            rowlist.append(row['initials'])
                            rowlist.append(row['name'])
                            rowlist.append(row['surname'])
                            rowlist.append(row['email'])
                            rowlist.append(row['cell'])
                            rowlist.append(row['user_id'])
                            rowlist.append(row['status'])
                            rowlist.append(row['password'])

                        if validate(row) == 2:
                            errortype = "Not all fields contain values."
                        if validate(row) == 3:
                            errortype = "Cell or user ID is not a number."
                        if validate(row) == 4:
                            errortype = "User already exists."

                        return render(request, 'peer_review/csvError.html',
                                      {'message': message, 'row': rowlist, 'error': errortype})
        else:
            form = DocumentForm()
            message = "Oops! Something seems to be wrong with the CSV file."
            errortype = "No file selected."
            return render(request, 'peer_review/csvError.html', {'message': message, 'row': rowlist})
    return HttpResponseRedirect('../')


def validate(row):
    # 0 = incorrect number of fields
    # 1 = correct
    # 2 = missing value/s
    # 3 = incorrect format
    # 4 = user already exists

    if len(row) < 9:
        return 0

    for key, value in row.items():
        if value is None:
            return 2

    for key, value in row.items():
        if key == "cell" or key == "user_id":
            try:
                int(value)
            except ValueError:
                return 3

    user = User.objects.filter(userId=row['user_id'])

    if user.count() > 0:
        return 4

    return 1





def getTypeID(questionType):
    # -1 = Error
    # 1 = Choice
    # 2 = Rank
    # 3 = Label
    # 4 = Rate
    # 5 = Freeform

    if questionType == "Choice":
        return 1
    elif questionType == "Rank":
        return 2
    elif questionType == "Label":
        return 3
    elif questionType == "Rate":
        return 4
    elif questionType == "Freeform":
        return 5
    else:
        return -1


def getGroupID(questionGroup):
    # -1 = Error
    # 1 = None
    # 2 = Rest
    # 3 = All

    if questionGroup == "None":
        return 1
    elif questionGroup == "Rest":
        return 2
    elif questionGroup == "All":
        return 3
    else:
        return -1

#QuestionAdmin stuff
#Todo: Merge the questionUpdate and createQuestion functions
#Todo: Implement saving of freeform type and label type
#Todo: Fix saving of rank type
#Todo: Save labels to DB when label grouping is selected

def questionUpdate(request):
    questionPk = request.GET['pk']
    question = Question.get(pk=questionPk)
    text = request.GET['question']
    qType = QuestionType.objects.get(name=request.GET['questionType'])

    #Choice
    if str(qType) == 'Choice':
        qGrouping = QuestionGrouping.objects.get(grouping=request.GET['grouping'])
        choices = request.GET.getlist('choices[]')
        #Save the question
        question.questionText=text
        question.pubDate=timezone.now() - datetime.timedelta(days=1)
        questionGrouping.questionGrouping=qGrouping
        question.save()

        #Save the choices
        rank = 0
        for choice in choices:
            c = Choice(question = q,
                       choiceText = choice,
                       num = rank,
                       header_id = 0)
            rank += 1
            c.save()

    #Rank
    elif str(qType) == 'Rank':
        qGrouping = QuestionGrouping.objects.get(grouping=request.GET['grouping'])
        wordOne = request.GET["firstWord"]
        wordTwo = request.GET["secondWord"]
        #Save the question
        question.questionText=text
        question.pubDate=timezone.now() - datetime.timedelta(days=1)
        questionGrouping.questionGrouping=qGrouping

        question.save()

        #Save the rank
        r = Rank(question=q,
                 firstWord=wordOne,
                 secondWord=wordTwo)
        r.save()


def getQuestion(request, questionPk):
    question = Question.objects.get(pk=questionPk)
    return JsonResponse({'questionText': question.questionText, 
                        'questionType': question.questionType.name,
                        'questionGrouping': question.questionGrouping.grouping,
                        })

def getChoices(request, questionPk):
    question = Question.objects.get(pk=questionPk)
    choices = Choice.objects.filter(question=question)
    response = {};
    for choice in choices:
        response[choice.num] = choice.choiceText
    # print(response)
    return JsonResponse(response)



def questionDelete(request, questionPk):
    question = Question.objects.get(pk=questionPk)
    question.delete()
    return HttpResponseRedirect('../')


def createQuestion(request):
    if 'question' in request.GET:
        text = request.GET['question']
        qType = QuestionType.objects.get(name=request.GET['questionType'])

        #Choice
        if str(qType) == 'Choice':
            qGrouping = QuestionGrouping.objects.get(grouping=request.GET['grouping'])
            choices = request.GET.getlist('choices[]')

            #Save the question
            q = Question(questionText = text,
                         pubDate = timezone.now() - datetime.timedelta(days=1),
                         questionType = qType,
                         questionGrouping = qGrouping
                         )
            q.save()

            #Save the choices
            rank = 0
            for choice in choices:
                c = Choice(question = q,
                           choiceText = choice,
                           num = rank,
                           header_id = 0)
                rank += 1
                # print(c)
                c.save()

        #Rank
        elif str(qType) == 'Rank':
            qGrouping = QuestionGrouping.objects.get(grouping=request.GET['grouping'])
            wordOne = request.GET["firstWord"]
            wordTwo = request.GET["secondWord"]

            #Save the question
            q = Question(questionText=text,
                         pubDate=timezone.now() - datetime.timedelta(days=1),
                         QuestionType=qType,
                         questionGrouping=qGrouping
                         )
            q.save()

            #Save the rank
            r = Rank(question=q,
                     firstWord=wordOne,
                     secondWord=wordTwo)
            r.save()
    else:
        message = 'You submitted an empty form.'
    return HttpResponse()

def roundDelete(request, roundPk):
    round = RoundDetail.objects.get(pk = roundPk)
    round.delete()
    return HttpResponseRedirect('../')

def roundUpdate(request, roundPk):
    if request.method == "POST":
        round = RoundDetail.objects.get(pk=roundPk)

        post_description = request.POST.get("description")
        post_questionnaire = request.POST.get("questionnaire")
        post_startingDate = request.POST.get("startingDate")
        post_endingDate = request.POST.get("endingDate")

        round.description = post_description
        round.questionnaire = post_questionnaire
        round.startingDate = post_startingDate
        round.endingDate = post_endingDate

        round.save()
    return HttpResponseRedirect('../')
