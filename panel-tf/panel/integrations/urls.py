from django.urls import path
from integrations.views import *


urlpatterns = [
    path('ct_hook', ct_hook),
    path('ms_hook', ms_hook),
]