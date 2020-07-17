from django.contrib import admin
from .views import QuestionPost, Comment
from .models import Registration, AccepterHistory, UserHistory
# Register your models here.
admin.site.register(QuestionPost)
admin.site.register(Comment)
admin.site.register(Registration)
admin.site.register(UserHistory)
admin.site.register(AccepterHistory)
