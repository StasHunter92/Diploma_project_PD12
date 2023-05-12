from django.db import models

from core.models import User
from goals.models.board import Board
from goals.models.mixins import DatesModelMixin


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class GoalCategory(DatesModelMixin):
    """Goal category model"""

    board = models.ForeignKey(
        Board, verbose_name="Доска", on_delete=models.PROTECT, related_name="categories"
    )
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    title = models.CharField(verbose_name="Название", max_length=255)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name: str = "Категория"
        verbose_name_plural: str = "Категории"

    def __str__(self) -> str:
        """Returns the title of a category"""
        return self.title
