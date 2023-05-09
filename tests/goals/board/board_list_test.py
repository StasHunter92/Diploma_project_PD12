from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.board import BoardCreateSerializer
from tests.factories import BoardFactory, BoardParticipantFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestBoardListView:
    """Tests for Board list view"""
    url: str = reverse('board_list')

    @pytest.mark.django_db
    def test_active_board_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can get a list of active boards,
        where user is a participant

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected board list

        Returns:
            None

        Raises:
            AssertionError
        """
        active_boards = BoardFactory.create_batch(size=5)

        for board in active_boards:
            BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = BoardCreateSerializer(active_boards, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert response.data == expected_response, 'Списки досок не совпадают'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_deleted_board_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user cannot get a list of deleted boards,
        where user is a participant

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User cannot get unexpected board list

        Returns:
            None

        Raises:
            AssertionError
        """
        deleted_boards = BoardFactory.create_batch(size=5, is_deleted=True)

        for board in deleted_boards:
            BoardParticipantFactory(board=board, user=user)

        unexpected_response: Dict = BoardCreateSerializer(deleted_boards, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert not response.data == unexpected_response, 'Получены удаленные доски'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_list_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot get a list of boards,
        where user is not a participant

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 200
            - User can not get unexpected board list

        Returns:
            None

        Raises:
            AssertionError
        """
        boards = BoardFactory.create_batch(size=5)

        for board in boards:
            BoardParticipantFactory(board=board)

        unexpected_response: Dict = BoardCreateSerializer(boards, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert not response.data == unexpected_response, 'Получены чужие доски'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_board_list_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the board list API endpoint

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

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
