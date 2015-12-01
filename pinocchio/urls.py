from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from peer_review import views

urlpatterns = [
                  url(r'^admin/', include(admin.site.urls)),
                  url(r'^fileUpload', views.fileUpload, name='fileUpload'),
                  url(r'^createQuestion/$', views.createQuestion, name='createQuestion'),
                  url(r'^maintainRound/$', views.maintainRound, name='maintainRound'),
                  
                  url(r'^maintainTeam/$', views.maintainTeam, name='maintainTeam'),
                  url(r'^questionnaireAdmin/$', views.questionnaireAdmin, name='questionnaireAdmin'),
		  url(r'^questionnaire/$', views.questionnaire, name='questionnaire'),

                  url(r'^$', views.index, name='index'),
                  url(r'^(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
                  url(r'^userAdmin/submitForm/?$', views.submitForm),
                  url(r'^userAdmin/submitCSV/$', views.submitCSV, name="submitCSV"),
                  url(r'^userAdmin/delete/(?P<userPk>[0-9]+)/?$', views.userDelete),
                  url(r'^userAdmin/update/(?P<userPk>[0-9]+)/?$', views.userUpdate),
                  url(r'^userAdmin/$', views.userList),
                  url(r'^questionAdmin/update/$', views.questionUpdate, name='questionUpdate'),
                  url(r'^questionAdmin/delete/$', views.questionDelete, name='questionDelete'),
                  url(r'^questionAdmin/getQuestion/(?P<questionPk>[0-9]+)/?$', views.getQuestion),
                  url(r'^questionAdmin/getChoices/(?P<questionPk>[0-9]+)/?$', views.getChoices),
                  url(r'^questionAdmin/getRank/(?P<questionPk>[0-9]+)/?$', views.getRank),
                  url(r'^questionAdmin', views.questionAdmin, name='questionAdmin'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
