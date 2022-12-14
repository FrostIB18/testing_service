from django.urls import path

from testing.views import themes, tests, questions, results

app_name = 'testing'

urlpatterns = [
    path('', themes, name='themes'),
    path('<int:theme_pk>/tests', tests, name='tests'),
    path('<int:theme_pk>/tests/<int:test_pk>', questions, name='questions'),
    path('<int:theme_pk>/tests/<int:test_pk>/questions/<int:page>', questions, name='page'),
    path('<int:theme_pk>/tests/<int:test_pk>/results', results, name='results')
]