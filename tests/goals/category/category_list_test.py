from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.board import BoardCreateSerializer
from goals.serializers.category import GoalCategorySerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCategoryListView:
    """Tests for GoalCategory list view"""

    url: str = reverse("category_list")

    @pytest.mark.django_db
    def test_active_category_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can get a list of active categories,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected category list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        active_categories = GoalCategoryFactory.create_batch(size=5, board=board)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalCategorySerializer(
            active_categories, many=True
        ).data
        sorted_expected_response: list = sorted(
            expected_response, key=lambda x: x["title"]
        )
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert (
            response.data == sorted_expected_response
        ), "Списки категорий не совпадают"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_category_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot get a list of deleted categories,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User cannot get unexpected category list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        deleted_categories = GoalCategoryFactory.create_batch(
            size=5, board=board, is_deleted=True
        )
        BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = GoalCategorySerializer(
            deleted_categories, many=True
        ).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.data == unexpected_response, "Получены удаленные категории"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_list_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot get a list of categories,
        where user is not a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 200
            - User can not get unexpected category list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        categories = GoalCategoryFactory.create_batch(size=5, board=board)
        BoardParticipantFactory(board=board)

        unexpected_response: Dict = BoardCreateSerializer(categories, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert not response.data == unexpected_response, "Получены чужие категории"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_list_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the category list API endpoint

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
