from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal_category import GoalCategory
from tests.factories import BoardFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCategoryCreateView:
    """Tests for GoalCategory create view"""

    url: str = reverse("category_create")

    @pytest.mark.django_db
    def test_category_create_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check if a new category can be created successfully,
        when the user is owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 201
            - Created category exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Owner category",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        created_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Категория не создалась"
        assert created_category, "Созданной категории не существует"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_create_viewer(self, authenticated_user, user) -> None:
        """
        Test to check if a new category cannot be created,
        when the user is viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 400
            - Unexpected category does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.viewer
        )

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Viewer category",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["board"][0] == "Вы не можете создавать категории"
        ), "Вы можете создать категорию"
        assert not unexpected_category, "Категория создана"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_create_deleted_board(self, authenticated_user, user) -> None:
        """
        Test to check if a new category cannot be created in the deleted board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 400
            - Unexpected category does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "board": board.pk,
            "title": "Deleted board category",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_category = GoalCategory.objects.filter(
            title=create_data["title"], board=board, user=user
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["board"][0] == "Доска удалена"
        ), "Вы можете создать категорию"
        assert not unexpected_category, "Категория создана"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_create_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the category create API endpoint

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
