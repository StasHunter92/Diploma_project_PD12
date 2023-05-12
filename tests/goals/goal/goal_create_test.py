from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from tests.factories import BoardFactory, BoardParticipantFactory, GoalCategoryFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestGoalCreateView:
    """Tests for Goal create view"""

    url: str = reverse("goal_create")

    @pytest.mark.django_db
    def test_goal_create_owner_moderator(
        self, authenticated_user, user, due_date
    ) -> None:
        """
        Test to check if a new goal can be created successfully,
        when the user is owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance
            due_date: A fixture that creates a date with the timedelta from the current date

        Checks:
            - Response status code is 201
            - Created goal exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        created_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Цель не создалась"
        assert created_goal, "Созданной цели не существует"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_create_viewer(self, authenticated_user, user, due_date) -> None:
        """
        Test to check if a new goal cannot be created,
        when the user is viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance
            due_date: A fixture that creates a date with the timedelta from the current date

        Checks:
            - Response status code is 400
            - Unexpected goal does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.viewer
        )

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["category"][0] == "Вы не можете создавать цели"
        ), "Вы можете создать цель"
        assert not unexpected_goal, "Цель создана"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_create_deleted_category(
        self, authenticated_user, user, due_date
    ) -> None:
        """
        Test to check if a new goal cannot be created in the deleted category

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance
            due_date: A fixture that creates a date with the timedelta from the current date

        Checks:
            - Response status code is 400
            - Unexpected goal does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board, is_deleted=True)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "category": category.pk,
            "title": "New goal",
            "due_date": due_date,
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_goal = Goal.objects.filter(
            user=user, category=category, title=create_data["title"]
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["category"][0] == "Категория удалена"
        ), "Вы можете создать цель"
        assert not unexpected_goal, "Цель создана"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_create_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the goal create API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        response: Response = api_client.post(self.url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
