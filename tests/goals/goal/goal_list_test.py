from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.goal import Goal
from goals.serializers.goal import GoalSerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, GoalFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestGoalListView:
    """Tests for Goal list view"""

    url: str = reverse("goal_list")

    @pytest.mark.django_db
    def test_active_goal_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can get a list of active goals,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected goal list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        active_goals = GoalFactory.create_batch(size=5, category=category)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalSerializer(active_goals, many=True).data
        sorted_expected_response: list = sorted(
            expected_response, key=lambda x: x["priority"]
        )
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.data == sorted_expected_response, "Списки целей не совпадают"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_goal_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot get a list of deleted goals,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User cannot get unexpected goal list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        deleted_goals = GoalFactory.create_batch(
            size=5, category=category, status=Goal.Status.archived
        )
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalSerializer(deleted_goals, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.data == unexpected_response, "Получены удаленные цели"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_list_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot get a list of goals,
        where user is not a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 200
            - User cannot get unexpected goal list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goals = GoalFactory.create_batch(size=5, category=category)
        BoardParticipantFactory(board=board)

        unexpected_response: Dict = GoalSerializer(goals, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.data == unexpected_response, "Получены чужие цели"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_list_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the goal list API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        response: Response = api_client.get(self.url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
