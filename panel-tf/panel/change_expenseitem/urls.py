from django.urls import path
from change_expenseitem.views import start

urlpatterns = [
    path('start', start),
]