from typing import Tuple

from django.db import models

from core.models import User
from goals.models.mixins import DatesModelMixin


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class Board(DatesModelMixin):
    """Board model"""

    title = models.CharField(verbose_name="Название", max_length=255)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name: str = "Доска"
        verbose_name_plural: str = "Доски"

    def __str__(self) -> str:
        """Returns the title of a board"""
        return self.title


# ----------------------------------------------------------------
class BoardParticipant(DatesModelMixin):
    """Participant model"""

    class Role(models.IntegerChoices):
        """Role choice"""

        owner = 1, "Владелец"
        moderator = 2, "Редактор"
        viewer = 3, "Читатель"

    board = models.ForeignKey(
        Board,
        verbose_name="Доска",
        on_delete=models.PROTECT,
        related_name="participants",
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.PROTECT,
        related_name="participants",
    )
    role = models.PositiveSmallIntegerField(
        verbose_name="Роль", choices=Role.choices, default=Role.owner
    )

    class Meta:
        unique_together: Tuple[str, ...] = ("board", "user")
        verbose_name: str = "Участник"
        verbose_name_plural: str = "Участники"

    def __str__(self) -> str:
        """Returns the username of a user"""
        return self.user.username
