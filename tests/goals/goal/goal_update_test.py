from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, GoalFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestGoalUpdateView:
    """Tests for Goal update view"""

    @pytest.mark.django_db
    def test_goal_update_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can update goal,
        where user is an owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can update the goal
            - Updated category exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse('goal', kwargs={'pk': goal.id})

        update_data: Dict[str, str] = {
            'title': 'New goal title',
            'category': category.id
        }

        response: Response = authenticated_user.put(url, data=update_data)
        updated_goal = Goal.objects.filter(
            title=update_data['title'],
            category=category
        ).exists()

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert response.data['title'] == update_data['title'], 'Обновленные данные не совпадают'
        assert updated_goal, 'Цель не обновлена'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_update_viewer(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot update goal,
        where user is a viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Only owner or moderator can update the goal
            - Unexpected goal does not exist in the database

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

        update_data: Dict[str, str] = {
            'title': 'New goal title',
            'category': category.id
        }

        response: Response = authenticated_user.put(url, data=update_data)
        unexpected_goal = Goal.objects.filter(
            title=update_data['title'],
            category=category
        ).exists()

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
        assert not unexpected_goal, 'Цель обновлена'
