from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.comment import GoalCommentSerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, GoalFactory, GoalCommentFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCommentListView:
    """Tests for GoalComment list view"""
    url: str = reverse('comment_list')

    @pytest.mark.django_db
    def test_comment_list_participant(self, authenticated_user, user) -> None:
        """
        Test to check that authenticated user can get a list of comments,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected comment list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comments = GoalCommentFactory.create_batch(size=5, goal=goal)
        BoardParticipantFactory(board=board, user=user)

        expected_response: Dict = GoalCommentSerializer(comments, many=True).data
        sorted_expected_response: list = sorted(expected_response, key=lambda x: x['created'])[::-1]
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert response.data == sorted_expected_response, 'Списки комментариев не совпадают'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_list_not_participant(self, authenticated_user) -> None:
        """
        Test to check that authenticated user cannot get a list of comments,
        where user is not a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 200
            - User cannot get unexpected comment list

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comments = GoalCommentFactory.create_batch(size=5, goal=goal)
        BoardParticipantFactory(board=board)

        unexpected_response: Dict = GoalCommentSerializer(comments, many=True).data
        response: Response = authenticated_user.get(self.url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert not response.data == unexpected_response, 'Получены чужие комментарии'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_list_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the comment list API endpoint

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
