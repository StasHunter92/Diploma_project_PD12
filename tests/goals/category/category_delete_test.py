import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from tests.factories import BoardFactory, GoalCategoryFactory, GoalFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCategoryDestroyView:
    """Tests for GoalCategory destroy view"""

    @pytest.mark.django_db
    def test_category_delete_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can delete category,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 204
            - User can delete the category
            - Categories change status 'is_deleted'
            - Goals change status to 'archived'

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse('category', kwargs={'pk': category.id})

        response: Response = authenticated_user.delete(url)
        category.refresh_from_db()
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT, 'Категория не удалена'
        assert category.is_deleted, 'Статус категории не обновился'
        assert goal.status == Goal.Status.archived, 'Статус цели не обновился'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_delete_viewer(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot delete category,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Viewer cannot delete the category
            - Categories does not change status 'is_deleted'
            - Goals does not change status to 'archived'

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
        url: str = reverse('category', kwargs={'pk': category.id})

        response: Response = authenticated_user.delete(url)
        category.refresh_from_db()
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
        assert not category.is_deleted, 'Статус категории обновился'
        assert not goal.status == Goal.Status.archived, 'Статус цели обновился'
