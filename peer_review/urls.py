from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^fileUpload', views.fileUpload, name='fileUpload'),
    url(r'^questionAdmin', views.questionAdmin, name='questionAdmin'),
    url(r'^createQuestion/$', views.createQuestion, name='createQuestion'),
    
    # ex: /peer_review/
    url(r'^$', views.index, name='index'),
    # ex: /peer_review/5/
    url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^userAdmin/submitForm/?$', views.submitForm),
    url(r'^userAdmin/submitCSV/$', views.submitCSV, name="submitCSV"),
    url(r'^userAdmin/delete/(?P<userPk>[0-9]+)/?$', views.userDelete),
    url(r'^userAdmin/update/(?P<userPk>[0-9]+)/?$', views.userUpdate),
    url(r'^userAdmin/$', views.userList),
]