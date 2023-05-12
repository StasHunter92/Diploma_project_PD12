import json
from typing import Dict, Union, List

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant, Board
from goals.serializers.board import BoardParticipantSerializer
from tests.factories import BoardFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestBoardUpdateView:
    """Tests for Board update view"""

    @pytest.mark.django_db
    def test_board_update_owner(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can update board, where user is an owner

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can update the board
            - Updated board exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse("board", kwargs={"pk": board.id})

        update_data: Dict[str, Union[str, List]] = {
            "participants": [],
            "title": "New title",
        }

        response: Response = authenticated_user.put(
            url, data=json.dumps(update_data), content_type="application/json"
        )

        updated_board = Board.objects.filter(title=update_data["title"]).exists()

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert (
            response.data["title"] == update_data["title"]
        ), "Обновленные данные не совпадают"
        assert updated_board, "Доска не обновлена"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_update_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot update board,
        where user is a moderator or a viewer

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 403
            - Only owner can update the board
            - Unexpected board does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        moderator_participant = BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.moderator
        )
        url: str = reverse("board", kwargs={"pk": board.id})
        participant = BoardParticipantSerializer(moderator_participant).data

        update_data: Dict[str, Union[str, List]] = {
            "participants": [participant],
            "title": "New title",
        }

        response: Response = authenticated_user.put(url, data=update_data)
        unexpected_board = Board.objects.filter(title=update_data["title"]).exists()

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не предоставлен"
        assert not unexpected_board, "Доска обновлена"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_update_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot update board,
        where user is not a participant

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        BoardParticipantFactory(board=board)
        url: str = reverse("board", kwargs={"pk": board.id})

        response: Response = authenticated_user.put(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, "Запрос дал результат"
