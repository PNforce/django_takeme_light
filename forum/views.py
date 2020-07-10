from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from .forms import QuestionPostForm, CommentForm, AddAcceptor
from .models import QuestionPost, Comment
from django.http.request import QueryDict
import inspect
from django.contrib.auth.decorators import login_required
from .lang import showstatebylang
from django.utils import timezone
from django.core.files.base import ContentFile

def get_index_page(request):
    return render(request, 'forum/home.html')

#__________________ process flow start ____________________________________
#start a request task

def get_task(request):
    msg, username ='', ''
    QueryDict_ask = QueryDict('', mutable=True)
    if request.method == 'POST':
        if 'username' in request.session:
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
            #ch state from null to open, wait set default value
            query = QuestionPost.objects.filter(id=request_id)
            query.update(state='open')
            url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
        else:
            print('is_valid() failed')
    else:
        print('provide form')
        form = QuestionPostForm()
    return render(request, 'forum/get_task.html', {'form': form})

#task page, send a request
#@login_required(login_url='/forum/login/')
def get_the_text(request, question_url_id, msg =''):
    query = QuestionPost.objects.filter(pk=question_url_id).values()
    ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
    querytwo = Comment.objects.filter(post_id=question_url_id)
    return render(request, 'forum/task_detail.html', {'query': query, 'querytwo': querytwo, 'ifvalue': ifvalue, 'msg':msg})

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

#check the rule of act can do or not at current state
def can_do_atstate_bool(act, now_state):
    result = False
    if now_state == 'open' and act == 'accept_task':
        result = True
    if (now_state == 'wait_pickup' or now_state == 'shipping') and act == 'task_received':
        result = True
    #open accept wait_confirm wait_pickup shipping arrived score
    return result

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
#@login_required(login_url='/forum/login/')
def accept_task(request, question_url_id):
    msg, bt_display ='', 'hidden'
    request_id = question_url_id
    query = QuestionPost.objects.filter(id=question_url_id)
    form = AddAcceptor()
    query_value = query.values()
    if is_sameperson_bool(request, question_url_id) == True:
        msg = "You can't accept your own request 無法接受自己發出的提案，請重新選擇please click delivery item "
        ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
        querytwo = Comment.objects.filter(post_id=question_url_id)
        return render(request, 'forum/task_detail.html',
                      {'query': query_value, 'querytwo': querytwo, 'ifvalue': ifvalue, 'msg': msg})

    state = list(query.values("state"))[0]['state']
    if can_do_atstate_bool('accept_task', state) == False:
        msg = '已有人接案'
        ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
        querytwo = Comment.objects.filter(post_id=question_url_id)
        print('in alreadfy')
        return render(request, 'forum/task_detail.html',
                      {'query': query_value, 'querytwo': querytwo, 'ifvalue': ifvalue, 'msg': msg})

    #can accept task and link to form page
    if request.method == "POST":
        form_update = query.first()
        form_update.accepter = str(request.session['username'])
        form_update.state = "wait_confirm"
        form_update.acceptmsg = request.POST['acceptmsg']
        form_update.save()
        url = reverse('forum:get_the_text', kwargs={'question_url_id': request_id})
        return HttpResponseRedirect(url)
    return render(request, 'forum/task_accept.html', {'form': form, 'request_id': '', 'msg': msg})

#the owner make confirm some one can delivery
def confirm_task(request, question_url_id):
    accepter, msg, acceptmsg, title, id = '', '', '', '', ''
    query = QuestionPost.objects.filter(id=question_url_id)
    accepter = list(query.values("accepter"))[0]['accepter']  #get string value
    acceptmsg = list(query.values("acceptmsg"))[0]['acceptmsg']
    title = list(query.values("title"))[0]['title']
    state = list(query.values("state"))[0]['state']
    id = question_url_id
    if request.method == "POST":
        if is_sameperson_bool(request, question_url_id) == True:
            if state == 'wait_pickup':
                msg = 'Allready checked 您已經同意過'
            elif state == 'open':
                msg = '還沒有人來取件'
            elif state != 'wait_confirm':
                msg = '無法操作'
            elif state == 'wait_confirm':
                str = 'wait_pickup'
                query.update(state=str)
        else:
            msg = 'Only task owner can agree 只有發案者可同意運送'
    return render(request, 'forum/task_confirm.html', {'accepter': accepter, 'acceptmsg': acceptmsg, 'state': state, 'title':title, 'id': id, 'msg': msg})

#accepter operate
def task_received(request, question_url_id):
    query, msg, s = '', '', ''
    query = QuestionPost.objects.filter(id=question_url_id)
    state = list(query.values("state"))[0]['state']
    print(state)
    act = 'task_received'
    if list(query.values("accepter"))[0]['accepter'] == request.session['username']:
        if can_do_atstate_bool(act, state):
            title = list(query.values("title"))[0]['title']
            msg = title + ' 物品送達'
            s = 'arrived'
            query.update(state=s)
        elif state == 'arrived' or state == 'score':
            msg = '物品已送達重複點選'
        else:
            msg ='無法操作'
    else:
        msg = 'Only responsible person operatre 只有接案者可操作'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})

#__________________ process flow end ____________________________________

#__________________ operate function start ____________________________________
def delete_task(request, question_url_id):
    msg = ''
    query = QuestionPost.objects.all()
    if is_sameperson_bool(request, question_url_id) == True:
        task = QuestionPost.objects.filter(id=question_url_id)
        task.delete()
    else:
        msg = 'Only delete your own task 無法刪除別人的委託'
    return render(request, 'forum/my_request_tasks.html', {'query': query, 'msg': msg})

def modify_task(request, question_url_id):
    msg = ''
    if is_sameperson_bool(request, question_url_id) == True:
        query = QuestionPost.objects.filter(id=question_url_id)
        title = list(query.values("title"))[0]['title']
        startloc = list(query.values("startloc"))[0]['startloc']
        endloc = list(query.values("endloc"))[0]['endloc']
        desc = list(query.values("desc"))[0]['desc']
        price = list(query.values("price"))[0]['price']
        state = list(query.values("state"))[0]['state']
        if request.method == "POST":
            msg = '改 call ok'
            query.update(title=request.POST['title'], startloc=request.POST['startloc'], endloc=request.POST['endloc'],
                          desc=request.POST['desc'], price=request.POST['price'])
    else:
        msg = 'Only modify your own task 無法更改別人的委託'
    return render(request, 'forum/task_modify.html', locals())

def cancel_task(request, question_url_id):
    query = QuestionPost.objects.filter(id=question_url_id)
    state = list(query.values("state"))[0]['state']
    if list(query.values("accepter"))[0]['accepter'] == request.session['username']:
        if state == 'wait_confirm' or state == 'wait_pickup':
            title = list(query.values("title"))[0]['title']
            msg = title + ' 物品取消運送成功'
            s = 'open'
            accepter = None
            query.update(state=s, accepter=accepter)
        else:
            msg = '無法取消，委託人已確認或已送達'
    else:
        msg = 'Only responsible person operatre 只有接案者可操作'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})
#__________________ operate function end ____________________________________

#__________________ page frame start ____________________________________
#show all tasks
def TasksOverview(request):
    query = QuestionPost.objects.all()
    return render(request, 'forum/AllTasks.html', {'query': query})

#@login_required(login_url='/forum/login/')
def my_request_tasks(request):
    query, msg = '', ''
    if 'username' in request.session:
        username =str(request.session['username'])
        query = QuestionPost.objects.filter(username=username)
    else:
        msg = '請先登入 please login first'
    return render(request, 'forum/my_request_tasks.html', {'query': query, 'msg':msg})

#@login_required(login_url='/forum/login/')
def my_responsible_tasks(request):
    query, msg = '', ''
    if 'username' in request.session:
        accepter = str(request.session['username'])
        query = QuestionPost.objects.filter(accepter=accepter)
    else:
        msg = '請先登入 please login first'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})
#__________________ page frame end ____________________________________

#For INVEST fun:
#print itself name and content
def p(var):
    import inspect
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    print(str([k for k, v in callers_local_vars if v is var][0])+': '+str(var))