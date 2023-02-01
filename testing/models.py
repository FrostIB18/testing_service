from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Theme(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()

    def __str__(self):
        return self.title


class Test_single(models.Model):
    title = models.CharField(max_length=350)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=1000)
    test = models.ForeignKey(Test_single, on_delete=models.CASCADE)
    max_points = models.FloatField()

    def __str__(self):
        return self.title


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    points = models.FloatField()

    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    test = models.ForeignKey(Test_single, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} | {self.question}'


class Results(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    test = models.ForeignKey(Test_single, on_delete=models.CASCADE)
    sum_points = models.FloatField()

    def __str__(self):
        return f'{self.user} | {self.test}'
