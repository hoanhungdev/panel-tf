"""panel URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt

from startpage.forms import CustomAuthForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(authentication_form=CustomAuthForm), name='login_url'),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout_url'),
    path('admin/', admin.site.urls),
    path('', include('startpage.urls')),
    path('info_lists/', include('info_lists.urls')),
    path('box_office/', include('box_office.urls')),
    path('start_project/', include('start_project.urls')),
    path('bank/', include('bank.urls')),
    path('create_project_folder/', include('create_project_folder.urls')),
    path('summary_table/', include('summary_table.urls')),
    path('bonuses/', include('bonuses.urls')),
    path('integrations/', include('integrations.urls')),
    path('change_expenseitem/', include('change_expenseitem.urls')),
    path('processingplan/', include('processingplan.urls')),
    path('check_store/', include('check_store.urls')),
    path('debiting_products/', include('debiting_products.urls')),
    path('stock_report/', include('stock_report.urls')),
    
]
