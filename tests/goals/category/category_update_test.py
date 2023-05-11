from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal_category import GoalCategory
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCategoryUpdateView:
    """Tests for GoalCategory update view"""

    @pytest.mark.django_db
    def test_category_update_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can update category,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can update the category
            - Updated category exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse('category', kwargs={'pk': category.id})

        update_data: Dict[str, str] = {
            'title': 'New category title',
            'board': board.id
        }

        response: Response = authenticated_user.put(url, data=update_data)
        updated_category = GoalCategory.objects.filter(
            title=update_data['title'],
            board=board
        ).exists()

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert response.data['title'] == update_data['title'], 'Обновленные данные не совпадают'
        assert updated_category, 'Категория не обновлена'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_update_viewer(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot update category,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Only owner or moderator can update the category
            - Unexpected category does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(
            board=board,
            user=user,
            role=BoardParticipant.Role.viewer
        )
        url: str = reverse('category', kwargs={'pk': category.id})

        update_data: Dict[str, str] = {
            'title': 'New category title'
        }

        response: Response = authenticated_user.put(url, data=update_data)
        unexpected_category = GoalCategory.objects.filter(
            title=update_data['title'],
            board=board
        ).exists()

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
        assert not unexpected_category, 'Категория обновлена'
