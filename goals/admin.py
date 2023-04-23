from django.contrib import admin

from goals.models.board import Board, BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory
from goals.models.goal_comment import GoalComment


# ----------------------------------------------------------------------------------------------------------------------
# Create admin models
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin settings for board"""
    list_display: tuple[str] = ('title', 'is_deleted')
    list_filter: tuple[str] = ('is_deleted',)
    readonly_fields: tuple[str] = ('created', 'updated')
    search_fields: tuple[str] = ('title',)
    search_help_text: str = 'Поиск по названию'


# ----------------------------------------------------------------
@admin.register(BoardParticipant)
class BoardParticipantAdmin(admin.ModelAdmin):
    """Admin settings for board participant"""
    list_display: tuple[str] = ('board', 'user', 'role')
    list_filter: tuple[str] = ('role', 'board', 'user')
    readonly_fields: tuple[str] = ('created', 'updated')

    fieldsets: tuple[tuple] = (
        ('Общая информация', {
            'fields': ('board', 'user', 'role')
        }),
        ('Информация о дате', {
            'fields': ('created', 'updated')
        }),
    )


# ----------------------------------------------------------------
@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    """Admin settings for goal category"""
    list_display: tuple[str] = ('title', 'user', 'created', 'updated', 'is_deleted')
    list_filter: tuple[str] = ('user', 'is_deleted')
    search_fields: tuple[str] = ('title', 'user__username')
    search_help_text: str = 'Поиск по названию или автору'
    readonly_fields: tuple[str] = ('user', 'created', 'updated')

    fieldsets: tuple[tuple] = (
        ('Общая информация', {
            'fields': ('user', 'title')
        }),
        ('Статус', {
            'fields': ('is_deleted',)
        }),
        ('Информация о дате', {
            'fields': ('created', 'updated')
        }),
    )


# ----------------------------------------------------------------
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin settings for goal"""
    list_display: tuple[str] = ('title', 'category', 'user', 'created', 'updated', 'status')
    list_filter: tuple[str] = ('user', 'category', 'status')
    search_fields: tuple[str] = ('title', 'category', 'user__username')
    search_help_text: str = 'Поиск по названию, категории или автору'
    readonly_fields: tuple[str] = ('user', 'created', 'updated')

    fieldsets: tuple[tuple] = (
        ('Общая информация', {
            'fields': ('user', 'title', 'description')
        }),
        ('Техническая информация', {
            'fields': ('category', 'status', 'priority')
        }),
        ('Информация о дате', {
            'fields': ('due_date', 'created', 'updated')
        }),
    )


# ----------------------------------------------------------------
@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    """Admin settings for goal comment"""
    list_display: tuple[str] = ('short_text', 'goal', 'user', 'created', 'updated')
    list_filter: tuple[str] = ('user', 'goal')
    search_fields: tuple[str] = ('text', 'goal__title', 'user__username')
    search_help_text: str = 'Поиск по цели, автору или тексту комментария'
    readonly_fields: tuple[str] = ('created', 'updated')

    fieldsets: tuple[tuple] = (
        ('Общая информация', {
            'fields': ('user', 'goal')
        }),
        ('Комментарий', {
            'fields': ('text',)
        }),
        ('Информация о дате', {
            'fields': ('created', 'updated')
        }),
    )

    @admin.display(description='Текст комментария')
    def short_text(self, comment):
        """Returns a short comment for preview"""
        return comment.text[:30] if len(comment.text) > 30 else comment.text
