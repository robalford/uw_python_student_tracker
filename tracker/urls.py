from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^$', views.create_report, name='create_report'),
    url(r'^progress-report/(?P<pk>\d+)/$', views.student_progress_report, name='progress_report'),
    url(r'^welcome-email/(?P<student_pk>\d+)/$', views.send_welcome_email, name='welcome_email'),
    url(r'^week-one-email/(?P<student_pk>\d+)/$', views.send_one_week_check_in, name='week_one_email'),
    url(
        r'^monthly-email/(?P<student_pk>\d+)/(?P<month_completed>\d+)/$',
        views.send_monthly_checkin,
        name='monthly_email'
    ),
]
