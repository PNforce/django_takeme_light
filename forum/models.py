from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
text = 'defaulttext'
class QuestionPost(models.Model):
    title = models.CharField(max_length=64, null=True)
    startloc = models.CharField(max_length=64, null=True)
    endloc = models.CharField(max_length=64, null=True)
    starttime = models.DateField(null=True, blank=True)
    endtime = models.DateField(null=True, blank=True)
    price = models.CharField(max_length=20, blank=True)
    desc = models.TextField(max_length=300, blank=True)
    file = models.ImageField()
    state = models.CharField(max_length=20, default='open')
    username = models.CharField(max_length=20, null=True)
    accepter = models.CharField(max_length=20, blank=True)
    acceptmsg = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    post = models.ForeignKey(QuestionPost, related_name='comments', on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

class Registration(models.Model):
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    username = models.CharField(max_length=200, null=True)
    password = models.CharField(max_length=200, null=True)
    activate = models.CharField(max_length=200, null=True)
    bday = models.DateField(auto_now_add=False, null=True)
    created_at = models.DateField(auto_now_add=True)
    activated = models.BooleanField(null=False, default=0)
    phone = models.CharField(max_length=13, null=True)

class UserHistory(models.Model):
    username = models.ForeignKey(Registration, on_delete=models.CASCADE)
    good_score = models.CharField(max_length=6, null=True)
    bad_score = models.CharField(max_length=6, null=True)
    accept_times = models.CharField(max_length=10, null=True)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)