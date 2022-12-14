from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
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

    test_sizes = {}
    for test in tests:
        questions = Question.objects.filter(test=test)
        test_size = len(questions)
        test_sizes[test.id] = test_size

    number_of_questions = len(questions)

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
    question = questions_paginator.object_list[0]

    choices = Choice.objects.filter(question=question)
    answers = Answer.objects.filter(user=request.user, theme=theme, test=test, question=question)

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
        dicts = []
        for el in range(len(request.POST.getlist('choice'))):
            dict = request.POST.copy()
            dict['choice'] = request.POST.getlist('choice')[el]
            dicts.append(dict)

        if len(request.POST.getlist('choice')) == 0:
            context.update({'answer': AnswerForm(), 'error':'Выберите хотя бы 1 вариант'})
            return render(request, 'testing/questions.html', context)
        elif len(request.POST.getlist('choice')) == len(choices):
            context.update({'answer': AnswerForm(), 'error': 'Выбор всех значений недопустим'})
            return render(request, 'testing/questions.html', context)
        elif len(request.POST.getlist('choice')) > question.max_points:
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
        return redirect(request.META.get('HTTP_REFERER','redirect_if_referer_not_found'))

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
    total_points = sum(answer.choice.points for answer in answers)
    max_points = sum(question.max_points for question in questions)

    total_points_percent = round(total_points/max_points*100, 2)
    if total_points_percent == 100:
        total_points_percent = int(total_points_percent)
    max_points_percent = 100

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