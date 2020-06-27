from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$', auth_views.LoginView, name='login'),
    url(r'^logout/$', auth_views.LoginView, name='logout'),
    url(r'^admin/', admin.site.urls),
]