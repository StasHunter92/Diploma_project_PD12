from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.category import GoalCategorySerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCategoryRetrieveView:
    """Tests for GoalCategory retrieve view"""

    @pytest.mark.django_db
    def test_active_category_retrieve_participant(
        self, authenticated_user, user
    ) -> None:
        """
        Test that authenticated user can get an active category,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected category

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("category", kwargs={"pk": category.id})

        expected_response: Dict = GoalCategorySerializer(category).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.data == expected_response, "Неправильная категория"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_category_retrieve_participant(
        self, authenticated_user, user
    ) -> None:
        """
        Test that authenticated user cannot get a deleted category,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 404
            - User cannot get unexpected category

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board, is_deleted=True)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("category", kwargs={"pk": category.id})

        unexpected_response: Dict = GoalCategorySerializer(category).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена удаленная категория"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_retrieve_not_participant(self, authenticated_user) -> None:
        """
        Test that authenticated user cannot get a single category, where user not a participant

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404
            - User cannot get unexpected category

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        BoardParticipantFactory(board=board)
        url: str = reverse("category", kwargs={"pk": category.id})

        unexpected_response: Dict = GoalCategorySerializer(category).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена чужая категория"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_category_retrieve_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access
        the category retrieve/update/destroy API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("category", kwargs={"pk": 1})

        response: Response = api_client.get(url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
