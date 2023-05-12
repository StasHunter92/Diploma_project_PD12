from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal_comment import GoalComment
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, GoalFactory, GoalCommentFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCommentUpdateView:
    """Tests for GoalComment update view"""

    @pytest.mark.django_db
    def test_comment_update_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test that authenticated user can update comment,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can update the comment
            - Updated comment exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comment = GoalCommentFactory(goal=goal)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("comment", kwargs={"pk": comment.id})

        update_data: Dict[str, str] = {"text": "Updated comment", "goal": goal.id}

        response: Response = authenticated_user.put(url, data=update_data)
        updated_comment = GoalComment.objects.filter(
            text=update_data["text"], goal=goal
        ).exists()

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert (
            response.data["text"] == update_data["text"]
        ), "Обновленные данные не совпадают"
        assert updated_comment, "Комментарий не обновлен"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_update_viewer(self, authenticated_user, user) -> None:
        """
        Test that authenticated user cannot update comment,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Only owner or moderator can update the comment
            - Unexpected comment does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comment = GoalCommentFactory(goal=goal)
        BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.viewer
        )
        url: str = reverse("comment", kwargs={"pk": comment.id})

        update_data: Dict[str, str] = {"text": "Updated comment", "goal": goal.id}

        response: Response = authenticated_user.put(url, data=update_data)
        unexpected_comment = GoalComment.objects.filter(
            text=update_data["text"], goal=goal
        ).exists()

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
        assert not unexpected_comment, "Комментарий обновлен"
