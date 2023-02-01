from django.contrib import admin

# Register your models here.
from testing.models import Theme, Test_single, Question, Choice, Answer, Results

admin.site.register(Theme)
admin.site.register(Test_single)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(Results)
