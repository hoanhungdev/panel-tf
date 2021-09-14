from django.urls import path
from processingplan.views import start

urlpatterns = [
    path('start', start)
]

