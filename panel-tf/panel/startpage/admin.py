from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from startpage.models import *
#from moysklad.services.entities.customentity import get_customentity_items


admin.site.register(Day)
admin.site.register(Auth)
admin.site.register(InputType)
admin.site.register(Input)


class UserInline0(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Инициалы'

class UserInline1(admin.StackedInline):
    model = MoyskladUser
    can_delete = False
    verbose_name_plural = 'Идентификатор пользователя в МоёмСкладе'

class UserInline2(admin.StackedInline):
    model = BitrixUser
    can_delete = False
    verbose_name_plural = 'Идентификатор пользователя в Битрикс 24'

# Определяем новый класс настроек для модели User
class UserAdmin(UserAdmin):
    inlines = (UserInline0, UserInline1, UserInline2,)

# Перерегистрируем модель User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ProjectGroupAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        self.change_form_template = 'admin/projectgroup_form.html'
        context.update({'b24_auth': Auth.get('bitrix')[0]})
        context.update({'project_types': get_customentity_items(id='7d84a4e4-0664-11e7-7a69-971100083b11')})
        return super(ProjectGroupAdmin, self).render_change_form(request,
            context, *args, **kwargs)

admin.site.register(ProjectGroup, ProjectGroupAdmin)

