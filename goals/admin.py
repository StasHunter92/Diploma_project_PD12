from django.contrib import admin

from goals.models import GoalCategory, Goal


class BaseAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'created', 'updated']
    search_fields = ['title', 'user']


class GoalCategoryAdmin(BaseAdmin):
    list_display = ['title', 'user', 'created', 'updated', 'is_deleted']


class GoalAdmin(BaseAdmin):
    pass


# ----------------------------------------------------------------------------------------------------------------------
# Register models
admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
