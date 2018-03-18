from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.create_report, name='create_report'),
    url(r'^progress-report/(?P<pk>\d+)/$', views.student_progress_report, name='progress_report'),
]
