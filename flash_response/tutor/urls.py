from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'tutor.views.welcome'),
    url(r'^select_course/$', 'tutor.views.select_course'),
    url(r'^sessions/$', 'tutor.views.sessions'),
    url(r'^sessions/new/$', 'tutor.views.new_session'),
    url(r'^sessions/(?P<session_id>\d+)/$', 'tutor.views.edit_session'),
    url(r'^sessions/(?P<session_id>\d+)/questions/add/$', 'tutor.views.new_question'),
    url(r'^sessions/(?P<session_id>\d+)/questions/edit/(?P<question_id>\d+)/$', 'tutor.views.edit_question'),
)