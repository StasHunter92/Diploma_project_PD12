from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import Board, BoardParticipant


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestBoardCreateView:
    """Tests for Board create view"""

    url: str = reverse("board_create")

    @pytest.mark.django_db
    def test_board_create(self, authenticated_user, user) -> None:
        """
        Test to check if a new board can be created successfully,
        when the user is authenticated

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 201
            - Created board exists in the database
            - Created BoardParticipant object exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        create_data: Dict[str, str] = {"title": "New board"}

        response: Response = authenticated_user.post(self.url, data=create_data)

        created_board = Board.objects.filter(title=create_data["title"]).exists()
        created_board_participant = BoardParticipant.objects.filter(
            board=created_board, user=user, role=BoardParticipant.Role.owner
        ).exists()

        assert response.status_code == status.HTTP_201_CREATED, "Доска не создалась"
        assert created_board, "Созданной доски не существует"
        assert created_board_participant, "Созданного участника не существует"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_create_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the board create API endpoint

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
