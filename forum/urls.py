"""exenv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views, auth
from django.conf.urls.static import static
from django.conf import settings


admin.autodiscover()
app_name = 'forum'
urlpatterns = [
    url(r'^$', views.get_index_page, name='get_index_page'),
    url(r'^get_task/$', views.get_task, name='get_task'),
    url(r'^recent/$', views.recent_questions, name='recent_questions'),
    url(r'^AllTasks/$', views.TasksOverview, name='TasksOverview'),
    url(r'^view/(?P<question_url_id>[0-9]+)/$', views.detail_task, name='detail_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/comment/$', views.add_comment_to_post, name='add_comment_to_post'),
    url(r'^view/(?P<question_url_id>[0-9]+)/accept/$', views.accept_task, name='accept_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/delete/$', views.delete_task, name='delete_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/modify/$', views.modify_task, name='modify_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/confirm/$', views.confirm_task, name='confirm_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/score/$', views.score_task, name='score_task'),
    url(r'^view/(?P<user_name>\S+)/user_info/$', views.user_info, name='user_info'),
    url(r'^my_tasks/$', views.my_request_tasks, name='my_request_tasks'),
    url(r'^my_responsible/$', views.my_responsible_tasks, name='my_responsible_tasks'),
    url(r'^view/(?P<question_url_id>[0-9]+)/cancel/$', views.cancel_task, name='cancel_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/shipping/$', views.shipping_task, name='shipping_task'),
    url(r'^view/(?P<question_url_id>[0-9]+)/received_task/$', views.received_task, name='received_task'),
    url(r'^login/$', auth.login, name='login'),
    url(r'^register/$', auth.register, name='register'),
    url(r'^logout/$', auth.logout, name='logout'),
    url(r'^check/$', auth.checkpage, name='check'),
    url(r'^activate/(?P<id>[^/?]+)/(?P<activation>[^/?]+)$', auth.activate, name='activate'),
    url(r'^mail/(?P<user_id>[^/?]+)/(?P<email>[^/?]+)/(?P<activate>[^/?]+)/$', auth.mail, name='mail'),
    url(r'^btdt/', auth.btdt, name='btdt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#    url(r'^view/(?P<question_url_id>[0-9]+)/accepttask/$', views.accepttask, name='accepttask'),