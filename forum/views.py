from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.http import HttpResponseRedirect
from .forms import QuestionPostForm, CommentForm, AddAcceptor
from .models import QuestionPost, Comment, AccepterHistory, UserHistory, Registration
from django.db.models import Avg
from django.http.request import QueryDict

import inspect
from django.contrib.auth.decorators import login_required
from .lang import showstatebylang
from django.utils import timezone
from django.core.files.base import ContentFile


def get_index_page(request):
    return render(request, 'forum/home.html')

# __________________ process flow start ____________________________________
# start a request task

def get_task(request):
    msg, username = '', ''
    QueryDict_ask = QueryDict('', mutable=True)
    if request.method == 'POST':
        if 'username' in request.session:
            username = str(request.session['username'])
            request.POST._mutable = True  # need change to mutable
            QueryDict_ask = request.POST
            QueryDict_ask.update({'username': username})
            form = QuestionPostForm(QueryDict_ask, request.FILES)
        else:
            msg = '請先登入 login first please'
            print('login first')
            return render(request, 'forum/get_task.html', {'msg': msg})

        if form.is_valid():
            form = form.save()
            request_id = form.id
            form.save()
            # ch state from null to open, wait set default value
            query = QuestionPost.objects.filter(id=request_id)
            query.update(state='open')
            url = reverse('forum:detail_task', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
        else:
            print('is_valid() failed')
    else:
        print('provide form')
        form = QuestionPostForm()
    return render(request, 'forum/get_task.html', {'form': form})


# task page, send a request
# @login_required(login_url='/forum/login/')
def detail_task(request, question_url_id, msg=''):
    query = QuestionPost.objects.filter(pk=question_url_id).values()
    ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
    querytwo = Comment.objects.filter(post_id=question_url_id)
    return render(request, 'forum/task_detail.html',
                  {'query': query, 'querytwo': querytwo, 'ifvalue': ifvalue, 'msg': msg})


# on the task page
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
            url = reverse('forum:detail_task', kwargs={'question_url_id': request_id})
            return HttpResponseRedirect(url)
    else:
        form = CommentForm()
        request_id = question_url_id
    return render(request, 'forum/add_comment_to_post.html', {'form': form, 'request_id': request_id})


def recent_questions(request):
    last_ten = QuestionPost.objects.order_by('created')[:10]
    last_ten_in_ascending_order = reversed(last_ten)
    return render(request, 'forum/recent_post.html', {'last_ten_in_ascending_order': last_ten_in_ascending_order})


# for accept task func:
def update_db(**kwargs):
    model_name = kwargs['model_name']
    id = kwargs['id']
    form_update = model_name.objects.filter(id=id).first()
    list_keys = kwargs.keys()
    for key in list_keys:
        if key != 'id' or 'model_name':
            form_update.key = kwargs[str(key)]
    form_update.save()


# check the rule of act can do or not at current state
def can_do_atstate_bool(act, now_state):
    result = False
    if act == 'delete_task':
        if now_state == ('open' or 'wait_confirm'):
            result = True
    elif act == 'modify_task':
        if now_state == ('open' or 'wait_confirm'):
            result = True
    elif act == 'confirm_task':
        if now_state == 'wait_confirm':
            result = True
    elif act == 'accept_task':
        if now_state == 'open':
            result = True
    elif act == 'cancel_pickup':
        if now_state == ('wait_confirm' or 'wait_pickup'):
            result = True
    elif act == 'received_task':
        if now_state == ('wait_pickup' or 'shipping'):
            result = True
    elif act == 'score_task':
        if now_state == 'arrived':
            result = True
    # open  wait_confirm wait_pickup shipping arrived score
    return result

# control the auth of CRUD actions
def is_sameperson_bool(request, question_url_id):
    # accepter ==user?
    db_username = QuestionPost.objects.filter(pk=question_url_id).values("username")
    a = list(db_username)
    if str(request.session['username']) == a[0]['username']:
        result = True
    else:
        result = False
    return result


# task/accept_task
# @login_required(login_url='/forum/login/')
def accept_task(request, question_url_id):
    msg, bt_display = '', 'hidden'
    request_id = question_url_id
    query = QuestionPost.objects.filter(id=question_url_id)
    form = AddAcceptor()
    query_value = query.values()

    if 'username' not in request.session:
        msg = "請先登入 Login first"
        return render(request, 'forum/task_detail.html',
                      {'query': query_value, 'querytwo': "", 'ifvalue': "", 'msg': msg})

    if is_sameperson_bool(request, question_url_id) == True:
        msg = "You can't accept your own request 無法接受自己發出的提案，請重新選擇please click delivery item "
        return render(request, 'forum/task_detail.html',
                      {'query': query_value, 'querytwo': "", 'ifvalue': "", 'msg': msg})

    state = list(query.values("state"))[0]['state']
    if can_do_atstate_bool('accept_task', state) == False:
        msg = '已有人接案'
        ifvalue = QuestionPost.objects.filter(pk=question_url_id, file='None').exists()
        querytwo = Comment.objects.filter(post_id=question_url_id)
        print('in alreadfy')
        return render(request, 'forum/task_detail.html',
                      {'query': query_value, 'querytwo': querytwo, 'ifvalue': ifvalue, 'msg': msg})

    # can accept task and link to form page
    if request.method == "POST":
        form_update = query.first()
        form_update.accepter = str(request.session['username'])
        form_update.state = "wait_confirm"
        form_update.acceptmsg = request.POST['acceptmsg']
        form_update.save()
        url = reverse('forum:detail_task', kwargs={'question_url_id': request_id})
        return HttpResponseRedirect(url)
    return render(request, 'forum/task_accept.html', {'form': form, 'request_id': '', 'msg': msg})


# the owner make confirm some one can delivery
def confirm_task(request, question_url_id):

    #read task info
    accepter, msg, acceptmsg, title, id = '', '', '', '', ''
    accept_score_service, accept_score_speed, accept_score_all, accept_times, accepter_id = '', '', '', '', ''
    query = QuestionPost.objects.filter(id=question_url_id)
    accepter = list(query.values("accepter"))[0]['accepter']  # get string value
    acceptmsg = list(query.values("acceptmsg"))[0]['acceptmsg']
    title = list(query.values("title"))[0]['title']
    state = list(query.values("state"))[0]['state']
    id = question_url_id
    act = 'confirm_task'

    #read accepter score record
    accept_score_service, accept_score_speed, accept_score_all, accept_times, accepter_id = read_accepter_score(accepter)

    #agree accepter come to pickup stuff
    if is_sameperson_bool(request, question_url_id) == True:
        if can_do_atstate_bool(act, state) == True:
            if request.method == "POST":
                str = 'wait_pickup'
                query.update(state=str)
                msg = '完成同意取件'
                p(request)
                return render(request, 'forum/task_confirm.html',
                              {'accepter': accepter, 'acceptmsg': acceptmsg, 'state': state, 'title': title, 'id': id,
                               'msg': msg})
            """
            elif request.method == "GET":
                str = 'open'
                msg = '重新等待接案'
                p(request)
                query.update(state=str, accepter='')
                return render(request, 'forum/task_confirm.html',
                              {'accepter': accepter, 'acceptmsg': acceptmsg, 'state': state, 'title': title, 'id': id,
                               'msg': msg})
            """
        elif state == 'wait_pickup':
            msg = 'Allready checked 您已經同意過'
        elif state == 'open':
            msg = '等待取件'
        elif state != 'wait_confirm':
            msg = '無法操作'
    else:
        msg = 'Only task owner can agree 只有發案者可同意運送'
    #return render(request, 'forum/task_confirm.html',{'accepter': accepter, 'acceptmsg': acceptmsg, 'state': state, 'title': title, 'id': id, 'msg': msg})
    return render(request, 'forum/task_confirm.html',locals())

# accepter operate
def received_task(request, question_url_id):
    query, msg, s = '', '', ''
    query = QuestionPost.objects.filter(id=question_url_id)
    state = list(query.values("state"))[0]['state']
    act = 'received_task'
    if list(query.values("accepter"))[0]['accepter'] == request.session['username']:
        if can_do_atstate_bool(act, state):
            title = list(query.values("title"))[0]['title']
            msg = title + ' 物品送達'
            s = 'arrived'
            query.update(state=s)
        elif state == 'arrived' or state == 'score':
            msg = '物品已送達重複點選'
        else:
            msg = '無法操作'
    else:
        msg = 'Only responsible person operatre 只有接案者可操作'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})
# __________________ process flow end ____________________________________

# __________________ operate function start ____________________________________
def delete_task(request, question_url_id):
    msg = ''
    query = QuestionPost.objects.all()
    act = 'delete_task'
    state = list(query.values("state"))[0]['state']
    if is_sameperson_bool(request, question_url_id) == True:
        if can_do_atstate_bool(act, state) == True:
            task = QuestionPost.objects.filter(id=question_url_id)
            # add pop-up warning
            task.delete()
        else:
            msg == '只有在未接案階段，請先取消原有委託'
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
            act = 'modify_task'
            if can_do_atstate_bool(act, state) == True:
                msg = '改 call ok'
                query.update(title=request.POST['title'], startloc=request.POST['startloc'],
                             endloc=request.POST['endloc'],
                             desc=request.POST['desc'], price=request.POST['price'])
                url = reverse('forum:my_request_tasks')
                #alert pop('修改完成')
                return HttpResponseRedirect(url)
            else:
                msg = '只能在未有人取件前作修改'
    else:
        msg = 'Only modify your own task 無法更改別人的委託'
    return render(request, 'forum/task_modify.html', locals())


def cancel_task(request, question_url_id):
    query = QuestionPost.objects.filter(id=question_url_id)
    state = list(query.values("state"))[0]['state']
    act = 'cancel_task'
    if list(query.values("accepter"))[0]['accepter'] == request.session['username']:
        if can_do_atstate_bool(act, state):
            title = list(query.values("title"))[0]['title']
            msg = title + ' 物品取消運送成功'
            s = 'open'
            accepter = ''
            query.update(state=s, accepter=accepter)
        else:
            msg = '無法取消，委託人已確認或已送達'
    else:
        msg = 'Only responsible person operatre 只有接案者可操作'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})


def score_task(request, question_url_id):
    msg, key_isuser, username, accepter = '', '', '', ''
    login_user = request.session['username']
    msg_repeat_score = '重複評分，回到上頁'

    #load score page initial
    query = QuestionPost.objects.filter(id=question_url_id)
    username = list(query.values("username"))[0]['username']
    accepter = list(query.values("accepter"))[0]['accepter']
    title = list(query.values("title"))[0]['title']
    state = list(query.values("title"))[0]['title']
    #if repeat score redirect to original page
    if username == login_user:
        history = AccepterHistory.objects.filter(id=question_url_id)
        if history.exists():
            print('repeat so redirect')
            #redirect('forum:my_request_tasks', msg=msg_repeat_score)
        #return render(request, 'forum/my_request_tasks.html', msg=msg_repeat)
        return render(request, 'forum/my_request_tasks.html', {'query': '', 'msg': msg_repeat_score})
    elif accepter == login_user:
        history = UserHistory.objects.filter(id=question_url_id)
        if history.exists():
            print('repeat so redirect')
        return render(request, 'forum/my_request_tasks.html', {'query': '', 'msg': msg_repeat_score})

    if is_sameperson_bool(request, question_url_id) == True:
        key_isuser = 'y'

    #read post info and write into db
    if request.method == "POST":
        score_speed = request.POST['radio_score_speed']
        score_service = request.POST['radio_score_service']
        score_all = request.POST['radio_score_all']
        score_desc = request.POST['desc']
        login_user = request.session['username']
        task_id = question_url_id
        msg = '評分成功'
        #score each other
        if username == login_user:
            history = AccepterHistory.objects.filter(id=task_id) # can delete?
            res = Registration.objects.get(username=accepter)
            accepter_db = AccepterHistory.objects.create(score_speed=score_speed, score_service=score_service, score_all=score_all, score_desc=score_desc,task_id=task_id, Accepter=res)
        elif accepter == login_user:
            res = Registration.objects.get(username=username)
            user_db = UserHistory.objects.create(score_speed=score_speed, score_service=score_service, score_all=score_all,task_id=task_id, score_desc=score_desc, user=res)
    return render(request, 'forum/task_score.html', locals())

# __________________ operate function end ____________________________________
# __________________ page frame start ____________________________________


# show all tasks
def TasksOverview(request):
    query = QuestionPost.objects.all()
    return render(request, 'forum/AllTasks.html', {'query': query})


# @login_required(login_url='/forum/login/')
def my_request_tasks(request, msg=''):
    query, msg, key_arrived = '', '', ''
    if 'username' in request.session:
        if request.method == "GET":
            print('get str by GET')
            print(request.GET.get('msg'))
            #wait to add msg repeat
        username = str(request.session['username'])
        query = QuestionPost.objects.filter(username=username)
        #state = list(query.values("state"))[0]['state']
        #key_arrived = 'y'
    else:
        msg = '請先登入 please login first'
    return render(request, 'forum/my_request_tasks.html', locals())


def my_responsible_tasks(request):
    query, msg = '', ''
    if 'username' in request.session:
        accepter = str(request.session['username'])
        query = QuestionPost.objects.filter(accepter=accepter)
    else:
        msg = '請先登入 please login first'
    return render(request, 'forum/my_responsible_tasks.html', {'query': query, 'msg': msg})
# __________________ page frame end ____________________________________

# __________________ score func start ____________________________________
def user_info(request, user_name):
    msg = ''
    username, send_times, send_score_service, send_score_speed, send_score_all = '', '', '', '', ''
    accept_times, accept_score_service, accept_score_speed, accept_score_all, accepter_id = '', '', '', '', ''
    search_user_name = user_name

    if request.method == "POST":
        keyin_search_user_name = request.POST['te_name']
        user_name = keyin_search_user_name
        search_user_name = keyin_search_user_name
    try:
        accept_score_service, accept_score_speed, accept_score_all, accept_times, accepter_id = read_accepter_score(search_user_name)
        user_id = accepter_id #in this case, find same person accept_score and send_score
        send_score_service, send_score_speed, send_score_all, send_times, user_id = read_user_score(search_user_name, user_id)
    except:
        user_name = '無此註冊用戶'
    # Find querydic from UserHistory
    """
    <h3>名稱name :  {{username}}</h3>
        <h4>送件-次數 : {{send_times}}</h4>
        <h4>送件-運送速度&準時 : {{send_score_service}}</h4>
        <h4>送件-服務態度&回復速度 : {{send_score_speed}}</h4>
        <h4>送件-整體評分 : {{send_score_all}}</h4>
    </table>
    <table class="table table-hover">
        <h4>接案-次數 : {{accept_times}}</h4>
        <h4>接案-運送速度&準時 : {{accept_score_service}}</h4>
        <h4>接案-服務態度&回復速度 : {{accept_score_speed}}</h4>
        <h4>接案-整體評分 : {{accept_score_all}}</h4>
    """
    return render(request, 'forum/user_info.html', locals())

#for user_info and task_confirm
def read_accepter_score(search_user_name, accepter_id=''):
    user_exist = True if search_user_name != '' else False
    if accepter_id =='':
        query = Registration.objects.filter(username=search_user_name)
        if query.exists():
            accepter_id = list(query.values("id"))[0]['id']
            acc_query = AccepterHistory.objects.filter(Accepter_id=accepter_id)
        else:
            user_exist = False
    # Find querydic from AccepterHistory

    if user_exist and acc_query.exists() :
        accept_times = len(list(acc_query.values("score_service")))
        accept_score_service = acc_query.aggregate(Avg('score_service'))['score_service__avg']
        accept_score_speed = acc_query.aggregate(Avg('score_speed'))['score_speed__avg']
        accept_score_all = acc_query.aggregate(Avg('score_all'))['score_all__avg']
        accept_times =''
        a = [accept_score_service, accept_score_speed, accept_score_all]
        z = map(lambda x: round(float(x), 1), [y for y in a])
        accept_score_service, accept_score_speed, accept_score_all = z
    else:
        accept_score_service, accept_score_speed, accept_score_all, accept_times = '-', '-', '-', '-'
    return accept_score_service, accept_score_speed, accept_score_all, accept_times, accepter_id

#for user_info
def read_user_score(search_user_name,user_id=''):
    user_exist = True if search_user_name != '' else False
    if user_id =='':
        query = Registration.objects.filter(username=search_user_name)
        if query.exists():
            user_id = list(query.values("id"))[0]['id']
        else:
            user_exist = False

    user_query = UserHistory.objects.filter(user_id=user_id)
    if user_exist and user_query.exists():
        send_times = len(list(user_query.values("score_service")))
        send_score_service = user_query.aggregate(Avg('score_service'))['score_service__avg']
        send_score_speed = user_query.aggregate(Avg('score_speed'))['score_speed__avg']
        send_score_all = user_query.aggregate(Avg('score_all'))['score_all__avg']
        send_times = ''
        a = [send_score_service, send_score_speed, send_score_all]
        z = map(lambda x: round(float(x), 1), [y for y in a])
        send_score_service, send_score_speed, send_score_all = z
    else:
        send_score_service, send_score_speed, send_score_all, send_times = '-', '-', '-', '-'
    return send_score_service, send_score_speed, send_score_all, send_times, user_id

# __________________ score func end ____________________________________
# For INVEST fun:
# print itself name and content
def p(*vars):
    import inspect
    for var in vars:
        callers_local_vars = inspect.currentframe().f_back.f_locals.items()
        print(str([k for k, v in callers_local_vars if v is var][0]) + ': ' + str(var))
