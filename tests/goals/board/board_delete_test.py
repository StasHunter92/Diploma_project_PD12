import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from tests.factories import BoardFactory, GoalCategoryFactory, GoalFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestBoardDestroyView:
    """Tests for Board destroy view"""

    @pytest.mark.django_db
    def test_board_delete_owner(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can delete board, where user is an owner

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 204
            - User can delete the board
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
        url: str = reverse('board', kwargs={'pk': board.id})

        response: Response = authenticated_user.delete(url)

        board.refresh_from_db()
        category.refresh_from_db()
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_204_NO_CONTENT, 'Доска не удалилась'
        assert board.is_deleted, 'Статус доски не поменялся'
        assert category.is_deleted, 'Статус категории не поменялся'
        assert goal.status == Goal.Status.archived, 'Статус цели не поменялся'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_delete_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot delete board,
        where user is a moderator or a viewer

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Only owner can delete the board
            - Board does not change status 'is_deleted'
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
        BoardParticipantFactory(board=board, user=user, role=BoardParticipant.Role.moderator)
        url: str = reverse('board', kwargs={'pk': board.id})

        response: Response = authenticated_user.delete(url)

        board.refresh_from_db()
        category.refresh_from_db()
        goal.refresh_from_db()

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
        assert not board.is_deleted, 'Статус доски поменялся'
        assert not category.is_deleted, 'Статус категории поменялся'
        assert not goal.status == Goal.Status.archived, 'Статус цели поменялся'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_delete_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot delete board,
        where user is not a participant

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board)
        url: str = reverse('board', kwargs={'pk': board.id})

        response: Response = authenticated_user.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, 'Запрос дал результат'
