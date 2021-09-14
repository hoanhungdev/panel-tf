from django.urls import path

from .views import start, update_table

urlpatterns = [
    path('start', start),
    path('update_table', update_table),
    
]