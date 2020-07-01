from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect, HttpResponse
from .forms import Validate, Register
from .models import Registration
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
# Create your views here.
def login(request):
    if request.method == 'POST':
        form = Validate(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            exists = Registration.objects.filter(username=username).exists()
            activated = Registration.objects.filter(username=username, activated=1).exists()
            if activated == True:
                if exists == True:
                    password_exists = Registration.objects.filter(username=username, password=password).exists()
                    if password_exists == True:
                        request.session['username'] = username
                        url = reverse('forum:check')
                        return HttpResponseRedirect(url)
                    else:
                        return HttpResponse('Password incorrect')
                else:
                    return HttpResponse('Username incorrect')
            else:
                return HttpResponse('account not active 帳號未啟用，請檢察郵箱')
    else:
        form = Validate()
        return render(request, 'forum/login.html', context=locals())

def register(request):
    if request.method == 'POST':
        key = get_random_string(length=32)
        form = Register(request.POST)
        if form.is_valid():
            query = Registration.objects.filter(username__iexact=form.cleaned_data['username']).exists()
            if query == True:
                return HttpResponse('Account name already exist 帳號已經存在')
            else:
                form = form.save()
                user_id = form.id
                email = form.email
                form.save()
                query = Registration.objects.filter(id=user_id).update(activate=key)
                url = reverse('forum:mail', args=[user_id, email, key])
            return HttpResponseRedirect(url)
    else:
        key = get_random_string(length=32)
        form = Register()
        return render(request, 'forum/login.html', context=locals())

def logout(request):
    try:
        del request.session['username']
    except:
        pass
    url = reverse('forum:get_index_page')
    return HttpResponseRedirect(url)

def checkpage(request):
    if request.session.has_key('username'):
        return HttpResponseRedirect(reverse('forum:get_index_page'))
    else:
        return HttpResponse('login fail登錄失敗')

def activate(request, id, activation):
    exist = Registration.objects.filter(id=id, activate=activation).exists()
    if exist == True:
        query = Registration.objects.filter(id=id).update(activated=1)
        return render(request, 'forum/activated.html', context=locals())
    else:
        return HttpResponse('Downie')
"""
def mail(request, user_id, email, activate):
    subject, from_email, to = 'Active your account at TakeMeThere NET', 'patrick110413@gmail.com', email
    text_content = 'This is an important message.'
    html_content = '<p>收信並點啟用連結</p><br><a href="http://127.0.0.1:8000/forum/activate/{0}/{1}">click here</a>'.format(user_id, activate)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
"""

def btdt(request):
    return render(request, 'forum/checkmail.html', context=locals())


#def sendMail(subject, body, html, to_addr):
def mail(request, user_id, email, activate) :
    from email.mime.text import MIMEText
    import smtplib
    print('now sending mail...')
    subject, from_addr, to_addr = 'Active your account at TakeMeThere NET', 'patrick110413@gmail.com', email
    html = '<p>收信並點啟用連結</p><br><a href="http://127.0.0.1:8000/forum/activate/{0}/{1}">click here</a>'.format(user_id, activate)
    mime: object = MIMEText(html, 'html', "utf-8")
    mime["Subject"] = subject
    mime["From"] = "PNforceStudio"
    mime["To"] = ""
    mime["Cc"] = ""
    msg = mime.as_string()
    smtpssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtpssl.login("patrick110413@gmail.com", "vbsqufevjocaxbkg")
    smtpssl.sendmail(from_addr, to_addr, msg, mail_options=(), rcpt_options=())
    smtpssl.quit()
    return HttpResponseRedirect('/forum/btdt/')