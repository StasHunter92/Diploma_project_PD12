from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment


# ----------------------------------------------------------------------------------------------------------------------
# Create admin models
@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    """Admin settings for goal category"""
    list_display: tuple[str] = ('title', 'user', 'created', 'updated', 'is_deleted')
    search_fields: tuple[str] = ('title', 'user__username')
    search_help_text: str = 'Поиск по категории или имени автора'


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin settings for goal"""
    list_display: tuple[str] = ('title', 'category', 'user', 'created', 'updated', 'status')
    search_fields: tuple[str] = ('title', 'category', 'user__username')
    search_help_text: str = 'Поиск по цели, категории или имени автора'


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    """Admin settings for goal comment"""
    list_display: tuple[str] = ('text', 'goal', 'user', 'created', 'updated')
    search_fields: tuple[str] = ('text', 'goal__title', 'user__username')
    search_help_text: str = 'Поиск по цели, имени автора или тексту комментария'

# ----------------------------------------------------------------------------------------------------------------------
# Register models
# admin.site.register(GoalCategory, GoalCategoryAdmin)
# admin.site.register(Goal, GoalAdmin)
# admin.site.register(GoalComment, GoalCommentAdmin)
