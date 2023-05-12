from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.board import BoardSerializer
from tests.factories import BoardFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestBoardRetrieveView:
    """Tests for Board retrieve view"""

    @pytest.mark.django_db
    def test_active_board_retrieve_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can get an active board,
        where user is a participant

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected board

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("board", kwargs={"pk": board.id})

        expected_response: Dict = BoardSerializer(board).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.data == expected_response, "Неправильная доска"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_board_retrieve_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot get a deleted board,
        where user is a participant

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 404
            - User cannot get unexpected board

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("board", kwargs={"pk": board.id})

        unexpected_response: Dict = BoardSerializer(board).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена удаленная доска"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_retrieve_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot get a board,
        where user is not a participant

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404
            - User cannot get unexpected board

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory(is_deleted=True)
        BoardParticipantFactory(board=board)
        url: str = reverse("board", kwargs={"pk": board.id})

        unexpected_response: Dict = BoardSerializer(board).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
        assert not response.data == unexpected_response, "Получена чужая доска"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_retrieve_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access
        the board retrieve/update/destroy API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("board", kwargs={"pk": 1})

        response: Response = api_client.get(url)

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
