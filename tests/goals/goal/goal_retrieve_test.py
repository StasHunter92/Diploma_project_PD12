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
class TestGoalRetrieveView:
    """Tests for Goal retrieve view"""

    @pytest.mark.django_db
    def test_active_goal_retrieve_participant(self, authenticated_user, user) -> None:
        """
        Test that authenticated user can get an active goal,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected goal

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("goal", kwargs={"pk": goal.id})

        expected_response: Dict = GoalSerializer(goal).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.data == expected_response, "Неправильная цель"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_goal_retrieve_participant(self, authenticated_user, user) -> None:
        """
        Test that authenticated user cannot get a deleted goal,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 404
            - User cannot get unexpected goal

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category, status=Goal.Status.archived)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("goal", kwargs={"pk": goal.id})

        unexpected_response: Dict = GoalSerializer(goal).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена удаленная цель"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_retrieve_not_participant(self, authenticated_user) -> None:
        """
        Test that authenticated user cannot get a single goal,
        where user not a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404
            - User cannot get unexpected goal

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(board=board)
        url: str = reverse("goal", kwargs={"pk": goal.id})

        unexpected_response: Dict = GoalSerializer(goal).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена чужая цель"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_retrieve_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access
        the goal retrieve/update/destroy API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("goal", kwargs={"pk": 1})

        response: Response = api_client.get(url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
