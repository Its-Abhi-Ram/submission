from django.urls import path
from . import views

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.login, name='login'),
    path('auth/monitoring-token/', views.monitoring_token, name='monitoring_token'),
    path('batches/', views.BatchListCreate.as_view(), name='batch_list_create'),
    path('batches/<int:id>/invite/', views.BatchInvite.as_view(), name='batch_invite'),
    path('batches/join/', views.join_batch, name='join_batch'),
    path('sessions/', views.SessionListCreate.as_view(), name='session_list_create'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('sessions/<int:id>/attendance/', views.session_attendance, name='session_attendance'),
    path('batches/<int:id>/summary/', views.batch_summary, name='batch_summary'),
    path('institutions/<int:id>/summary/', views.institution_summary, name='institution_summary'),
    path('programme/summary/', views.programme_summary, name='programme_summary'),
    path('monitoring/attendance/', views.monitoring_attendance, name='monitoring_attendance'),
]