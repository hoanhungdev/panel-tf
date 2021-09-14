from django.urls import path
from .views import *



urlpatterns = [
    path('', index, name='info_lists_url'),
    path('start', start),
    path('create_report', create_report),
    #path('load', load),
    #path('hide_alert/<int:alert_id>', hide_alert)
    #path('get_data', get_data),
    #path('get_periodic_tasks', PeriodicTaskView.as_view()),
]