from django.db import models

from core.models import User
from goals.models.goal_category import GoalCategory
from goals.models.mixins import DatesModelMixin


# ----------------------------------------------------------------------------------------------------------------------
# Create models
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

    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    category = models.ForeignKey(
        GoalCategory,
        verbose_name="Категория",
        on_delete=models.PROTECT,
        related_name="goals",
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.CharField(max_length=255, verbose_name="Описание", blank=True)
    status = models.PositiveSmallIntegerField(
        verbose_name="Статус", choices=Status.choices, default=Status.to_do
    )
    priority = models.PositiveSmallIntegerField(
        verbose_name="Приоритет", choices=Priority.choices, default=Priority.medium
    )
    due_date = models.DateField(verbose_name="Дата дедлайна", blank=True)

    class Meta:
        verbose_name: str = "Цель"
        verbose_name_plural: str = "Цели"

    def __str__(self) -> str:
        """Returns the title of a goal"""
        return self.title
