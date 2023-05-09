import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from tests.factories import BoardFactory, GoalCategoryFactory, GoalFactory, BoardParticipantFactory, GoalCommentFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestGoalDestroyView:
    """Tests for Goal destroy view"""

    @pytest.mark.django_db
    def test_goal_delete_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can delete goal,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 204
            - User can delete the goal
            - Goal change status to 'archived'
            - Goal comments delete from database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        GoalCommentFactory.create_batch(size=5, goal=goal)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse('goal', kwargs={'pk': goal.id})

        response: Response = authenticated_user.delete(url)
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT, 'Цель не удалена'
        assert goal.status == Goal.Status.archived, 'Статус цели не обновился'
        assert not goal.comments.exists(), 'Комментарии не удалились'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_delete_viewer(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot delete goal,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Viewer cannot delete the category
            - Goal does not change status to 'archived'

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(
            board=board,
            user=user,
            role=BoardParticipant.Role.viewer
        )
        url: str = reverse('goal', kwargs={'pk': goal.id})

        response: Response = authenticated_user.delete(url)
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
        assert not goal.status == Goal.Status.archived, 'Статус цели обновился'
