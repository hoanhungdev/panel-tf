from django.contrib import admin
from .models import *
from startpage.models import Auth

admin.site.register(DataInput)

#class ProjectTypeAdmin(admin.ModelAdmin):
#    def render_change_form(self, request, context, *args, **kwargs):
#        self.change_form_template = 'admin/projecttype_form.html'
#        context.update({'b24_auth': Auth.get('bitrix')[0]})
#        return super(ProjectTypeAdmin, self).render_change_form(request,
#            context, *args, **kwargs)
#
#admin.site.register(ProjectType, ProjectTypeAdmin)

