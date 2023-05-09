from typing import Dict

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.serializers.comment import GoalCommentSerializer
from tests.factories import BoardFactory, GoalCategoryFactory, BoardParticipantFactory, GoalFactory, GoalCommentFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCommentRetrieveView:
    """Tests for GoalComment retrieve view"""

    @pytest.mark.django_db
    def test_comment_retrieve_participant(self, authenticated_user, user) -> None:
        """
        Test that authenticated user can get a single comment,
        where user is a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 200
            - User can get expected comment

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comment = GoalCommentFactory(goal=goal)
        BoardParticipantFactory(board=board, user=user)
        url: str = reverse('comment', kwargs={'pk': comment.id})

        expected_response: Dict = GoalCommentSerializer(comment).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_200_OK, 'Запрос не прошел'
        assert response.data == expected_response, 'Неправильный комментарий'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_retrieve_not_participant(self, authenticated_user) -> None:
        """
        Test that authenticated user cannot get a single comment,
        where user not a participant of the board

        Args:
            authenticated_user: API client with authenticated user for testing

        Checks:
            - Response status code is 404
            - User cannot get unexpected comment

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        comment = GoalCommentFactory(goal=goal)
        BoardParticipantFactory(board=board)
        url: str = reverse('comment', kwargs={'pk': comment.id})

        unexpected_response: Dict = GoalCommentSerializer(comment).data
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND, 'Запрос дал результат'
        assert not response.data == unexpected_response, 'Получен чужой комментарий'

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_retrieve_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access
        the comment retrieve/update/destroy API endpoint

        Args:
            api_client: API client without user for testing

        Checks:
            - Response status code is 403

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse('comment', kwargs={'pk': 1})

        response: Response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Отказ в доступе не предоставлен'
