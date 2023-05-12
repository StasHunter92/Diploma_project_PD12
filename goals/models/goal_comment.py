from django.db import models

from core.models import User
from goals.models.goal import Goal
from goals.models.mixins import DatesModelMixin


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class GoalComment(DatesModelMixin):
    """Goal comment model"""

    goal = models.ForeignKey(
        Goal, verbose_name="Цель", on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.CASCADE)
    text = models.CharField(max_length=1000, verbose_name="Текст")

    class Meta:
        verbose_name: str = "Комментарий"
        verbose_name_plural: str = "Комментарии"

    def __str__(self) -> str:
        """Returns the text of a comment"""
        return self.text
