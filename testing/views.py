from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from testing.forms import AnswerForm
from testing.models import Theme, Test_single, Question, Choice, Answer, Results


def home(request):
    context = {
        'title':'Home'
    }
    return render(request, 'testing/home.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Вы успешно зарегестрировались!')
            auth.login(request, user)
            return HttpResponseRedirect(reverse('testing:themes'))
    else:
        form = UserCreationForm()
    context = {
        'title':'Регистрация',
        'form':form
    }
    return render(request, 'testing/signup.html', context)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username,password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('testing:themes'))
    else:
        form = AuthenticationForm()
    context = {
        'title':'Авторизация',
        'form':form
    }
    return render(request, 'testing/login.html', context)

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('home'))

@login_required
def themes(request):
    themes = Theme.objects.all()
    context = {
        'title':'Themes',
        'themes':themes
    }
    return render(request, 'testing/themes.html', context)

def tests(request, theme_pk):
    theme = Theme.objects.get(pk=theme_pk)
    tests = Test_single.objects.filter(theme=theme)

    #creates a dict for total number of questions for tests page (doesn't work - test_sizes.test.id doesn't work in django template)
    test_sizes = {}
    for test in tests:
        questions = Question.objects.filter(test=test)
        test_size = len(questions)
        test_sizes[test.id] = test_size

    context = {
        'title':'Tests',
        'theme':theme,
        'tests':tests,
        'test_sizes':test_sizes,
        'number_of_questions': number_of_questions
    }
    return render(request, 'testing/tests.html', context)

def questions(request, test_pk, theme_pk, page=1):

    theme = Theme.objects.get(pk=theme_pk)
    test = Test_single.objects.filter(theme=theme).get(pk=test_pk)
    questions = Question.objects.filter(test=test)

    paginator = Paginator(questions, 1)
    questions_paginator = paginator.page(page)
    question = questions_paginator.object_list[0] #first and only question for a page

    choices = Choice.objects.filter(question=question)
    answers = Answer.objects.filter(user=request.user, theme=theme, test=test, question=question)

    #just a list of answers id (need for displaying chosen choices and disabled send button after for submission
    answers_id = []
    for ans in answers:
        answers_id.append(ans.choice.id)

    context = {
        'title':test,
        'theme':theme,
        'test':test,
        'choices':choices,
        'page': page,
        'question':question,
        'answers_id':answers_id,
        'questions': questions,
        'questions_pag': questions_paginator,
    }

    if request.method == "POST":

        #creates a dicts list of current answers of user
        dicts = []
        answers_ids = request.POST.getlist('choice') #gets ids of user answers
        for el in range(len(answers_ids)):
            dict = request.POST.copy()
            dict['choice'] = answers_ids[el]
            dicts.append(dict)

        #a custom form validation
        if len(answers_ids) == 0:
            context.update({'answer': AnswerForm(), 'error':'Выберите хотя бы 1 вариант'})
            return render(request, 'testing/questions.html', context)
        elif len(answers_ids) == len(choices):
            context.update({'answer': AnswerForm(), 'error': 'Выбор всех значений недопустим'})
            return render(request, 'testing/questions.html', context)
        elif len(answers_ids) > question.max_points:
            context.update({'answer': AnswerForm(), 'error': f'Выберите {int(question.max_points)} значение/я', })
            return render(request, 'testing/questions.html', context)
        else:
            for dict in dicts:
                form = AnswerForm(dict)
                answer = form.save(commit=False)
                answer.user = request.user
                answer.theme = theme
                answer.test = test
                answer.question = question
                answer.save()
        return redirect(request.META.get('HTTP_REFERER','redirect_if_referer_not_found')) #refreshes a page after form submission

    context.update({
        'answers':answers,
    })
    return render(request, 'testing/questions.html', context)

def results(request, theme_pk, test_pk):

    user = request.user
    theme = Theme.objects.get(pk=theme_pk)
    test = Test_single.objects.filter(theme=theme).get(pk=test_pk)
    questions = Question.objects.filter(test=test)

    answers = Answer.objects.filter(user=user, test=test).select_related('choice').all()
    total_points = sum(answer.choice.points for answer in answers) #displays number of scored points for a user
    max_points = sum(question.max_points for question in questions) #displays max points for a test

    #point in percent
    total_points_percent = round(total_points/max_points*100, 2)
    if total_points_percent == 100:
        total_points_percent = int(total_points_percent)
    max_points_percent = 100

    #saving results in DB (page doesn't created)
    result = Results(user=user, theme=theme, test=test, sum_points=total_points)
    result.save()

    context = {
        'title':'Results',
        'theme':theme,
        'test':test,
        'total_points':total_points,
        'max_points':max_points,
        'total_points_percent':total_points_percent,
        'max_points_percent': max_points_percent,
    }
    return render(request, 'testing/results.html', context)