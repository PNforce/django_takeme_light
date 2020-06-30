from django import forms
from .models import Comment, QuestionPost, Registration
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
#Create your models here.

#ask page
class QuestionPostForm(forms.ModelForm):

    class Meta:
        model = QuestionPost
        fields = ('title', 'startloc', 'endloc', 'starttime', 'endtime', 'desc', 'price', 'file')

#<QueryDict: {'csrfmiddlewaretoken': ['1GfWcQByd95gS24J8SJ8Ylu23UezTDPYRf5ksHb5rYWOlM28Aww7DF5nbLb2w1nL'], 'title': ['123123'], 'startloc': ['tp'], 'endloc': ['ta'], 'starttime': ['2020'],
#'endtime': ['2021'], 'desc': ['1111000kg'], 'price': ['10000'], 'submit': ['提交']}>

#<MultiValueDict: {'file': [<InMemoryUploadedFile: screen-00.54.39[25.06.2020].png (image/png)>]}>

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text',)

class Validate(forms.ModelForm):

    class Meta:
        model = Registration
        fields = ('username', 'password')

class DateInput(forms.DateInput):
    input_type = 'date'

class Register(forms.ModelForm):

    class Meta:
        model = Registration
        exclude = ('activated','activate')
        widgets = {
            'bday': DateInput(),
        }