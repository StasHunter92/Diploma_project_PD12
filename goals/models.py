from django.db import models
from django.utils import timezone

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class DatesModelMixin(models.Model):
    """Abstract model for time-date conversion"""
    created = models.DateTimeField(verbose_name='Дата создания')
    updated = models.DateTimeField(verbose_name='Дата последнего обновления')

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            self.created = timezone.now()
        self.updated = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        abstract: bool = True


# ----------------------------------------------------------------
class GoalCategory(DatesModelMixin):
    """Goal category model"""
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.PROTECT)
    title = models.CharField(verbose_name='Название', max_length=255)
    created = models.DateTimeField(verbose_name='Дата создания')
    updated = models.DateTimeField(verbose_name='Дата последнего обновления')
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name: str = 'Категория'
        verbose_name_plural: str = 'Категории'


# ----------------------------------------------------------------
class Goal(DatesModelMixin):
    """Goal model"""

    class Status(models.IntegerChoices):
        """Status choice"""
        to_do = 1, "Запланировано"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        """Priority choice"""
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.PROTECT)
    category = models.ForeignKey(GoalCategory, verbose_name='Категория', on_delete=models.PROTECT)
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.CharField(max_length=255, verbose_name='Описание', blank=True)
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет', choices=Priority.choices,
                                                default=Priority.medium)
    due_date = models.DateField(verbose_name='Дата дедлайна', blank=True)
    created = models.DateTimeField(verbose_name='Дата создания')
    updated = models.DateTimeField(verbose_name='Дата последнего обновления')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name: str = 'Цель'
        verbose_name_plural: str = 'Цели'


# ----------------------------------------------------------------
class GoalComment(DatesModelMixin):
    """Goal comment model"""
    goal = models.ForeignKey(Goal, verbose_name='Цель', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000, verbose_name='Текст')
    created = models.DateTimeField(verbose_name='Дата создания')
    updated = models.DateTimeField(verbose_name='Дата последнего обновления')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name: str = 'Комментарий'
        verbose_name_plural: str = 'Комментарии'
