from django.urls import path
from .views import update_table, check_archive, save_table


urlpatterns = [
    path('update_table', update_table),
    path('check_archive', check_archive),
    path('save_table', save_table),
]



