import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from tests.factories import BoardFactory, GoalCategoryFactory, GoalFactory, BoardParticipantFactory, GoalCommentFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCommentDestroyView:
    """Tests for GoalComment destroy view"""

    @pytest.mark.django_db
    def test_comment_delete_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can delete goal,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 204
            - User can delete the goal
            - Goal comment delete from database

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

        response: Response = authenticated_user.delete(url)

        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Комментарий не удален"
        assert not goal.comments.exists(), "Комментарий существует"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_delete_viewer(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot delete comment,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Viewer cannot delete the comment
            - Goal comment does not delete from database

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

        response: Response = authenticated_user.delete(url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
        assert goal.comments.exists(), "Комментарий удалился"
