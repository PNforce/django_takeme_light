from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from .forms import QuestionPostForm, CommentForm, AddAcceptor
from .models import QuestionPost, Comment
from django.http.request import QueryDict
from django.utils import timezone
from django.core.files.base import ContentFile
# Create your views here.

def get_index_page(request):
    return render(request, 'forum/home.html')

def get_task(request):
    msg, username ='', ''
    QueryDict_ask = QueryDict('', mutable=True)
    if request.method == 'POST':
        print("request.POST")
        print(request.POST)

        print("request.FILES")
        print(request.FILES)
        if 'username' in request.session:
            print('IM in')
            username = str(request.session['username'])
            request.POST._mutable = True #need change to mutable
            QueryDict_ask = request.POST
            QueryDict_ask.update({'username': username})
            form = QuestionPostForm(QueryDict_ask, request.FILES)
        else:
            msg ='請先登入 login first please'
            print('login first')
            return render(request, 'forum/get_task.html', {'msg': msg})

        if form.is_valid():
            form = form.save()
            request_id = form.id
            form.save()
            url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
        else:
            print('is_valid() failed')
    else:
        print('provide form')
        form = QuestionPostForm()
    return render(request, 'forum/get_task.html', {'form': form})

def checkformvaildandsave(form):
    if form.is_valid():
        form = form.save()
        request_id = form.id
        form.save()
        url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
        return HttpResponseRedirect(url)
    else:
        print('is_valid() failed')

#task page
def get_the_text(request, question_url_id):
    query = QuestionPost.objects.filter(pk=question_url_id).values()
    ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
    querytwo = Comment.objects.filter(post_id=question_url_id)
    return render(request, 'forum/task.html', {'query': query, 'querytwo': querytwo, 'ifvalue': ifvalue})

def QuestionOversight(request):
    query = QuestionPost.objects.all()
    return render(request, 'forum/questions.html', {'query': query})

#on the task page
def add_comment_to_post(request, question_url_id):
    post = get_object_or_404(QuestionPost, pk=question_url_id)
    form = CommentForm()
    request_id = question_url_id
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
    else:
        form = CommentForm()
        request_id = question_url_id
    return render(request, 'forum/add_comment_to_post.html', {'form': form, 'request_id': request_id})

def recent_questions(request):
    last_ten = QuestionPost.objects.order_by('created')[:10]
    last_ten_in_ascending_order = reversed(last_ten)
    return render(request, 'forum/recent_post.html', {'last_ten_in_ascending_order': last_ten_in_ascending_order})

#for accept task func:
def update_db(**kwargs):
    model_name = kwargs['model_name']
    id = kwargs['id']
    form_update = model_name.objects.filter(id=id).first()
    list_keys = kwargs.keys()
    for key in list_keys:
        if key !='id' or 'model_name':
            form_update.key = kwargs[str(key)]
    form_update.save()

#control the auth of CRUD actions
def is_sameperson_bool(request, question_url_id):
    # accepter ==user?
    db_username = QuestionPost.objects.filter(pk=question_url_id).values("username")
    a = list(db_username)
    if str(request.session['username']) == a[0]['username']:
        result = True
        print('same person')
    else:
        result = False
        print('not person')
    return result

#task/accept_task
def accept_task(request, question_url_id):
    msg, bt_display ='', 'hidden'
    form = AddAcceptor()
    request_id = question_url_id
    if request.method == "POST":
        if is_sameperson_bool(request, question_url_id)==False:
            bt_display = "visible"
            #ORM operate
            form_update = QuestionPost.objects.filter(id=question_url_id).first()
            form_update.accepter = str(request.session['username'])
            form_update.state = "待確認wait confirm"
            form_update.acceptmsg = request.POST['acceptmsg']
            form_update.save()
            url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
        else:
            msg = "You can't accept your own request 無法接受自己發出的提案，請重新選擇please click delivery item "
            bt_display = "hidden"
            form = ''
            print('forbidden same person')
    return render(request, 'forum/accepttask.html', {'form': form, 'request_id': '', 'bt_display': bt_display, 'msg':msg})

def delete_task(request, question_url_id):
    msg = ''
    query = QuestionPost.objects.all()
    if is_sameperson_bool(request, question_url_id) == True:
        task = QuestionPost.objects.filter(id=question_url_id)
        task.delete()
    else:
        msg = 'Only delete your own task 無法刪除別人的委託'
    return render(request, 'forum/questions.html', {'query': query, 'msg': msg})

def modify_task(request, question_url_id):
    msg = ''
    query = QuestionPost.objects.all()
    if is_sameperson_bool(request, question_url_id) == True:
        msg = '改'
    else:
        msg = 'Only modify your own task 無法更改別人的委託'
    return render(request, 'forum/questions.html', {'query': query, 'msg': msg})
    #return render(request, 'forum/questions.html', {'query': query})

def confirm_task(request, question_url_id):
    pass

def my_tasks(request):
    query, msg = '', ''
    if 'username' in request.session:
        username =str(request.session['username'])
        query = QuestionPost.objects.filter(username=username)
    else:
        msg = '請先登入 please login first'
    return render(request, 'forum/my_tasks.html', {'query': query, 'msg':msg})