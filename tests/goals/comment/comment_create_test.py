from typing import Dict, Union

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_comment import GoalComment
from tests.factories import BoardFactory, BoardParticipantFactory, GoalCategoryFactory, GoalFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
class TestCommentCreateView:
    """Tests for GoalComment create view"""

    url: str = reverse("comment_create")

    @pytest.mark.django_db
    def test_comment_create_owner_moderator(self, authenticated_user, user) -> None:
        """
        Test to check if a new comment can be created successfully,
        when the user is owner or moderator of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

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
        goal = GoalFactory(category=category)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "goal": goal.id,
            "text": "New comment",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        created_comment = GoalComment.objects.filter(
            user=user, goal=goal, text=create_data["text"]
        ).exists()

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Комментарий не создался"
        assert created_comment, "Созданного комментария не существует"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_goal_create_viewer(self, authenticated_user, user) -> None:
        """
        Test to check if a new comment cannot be created,
        when the user is viewer of the board

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 400
            - Unexpected comment does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category)
        BoardParticipantFactory(
            board=board, user=user, role=BoardParticipant.Role.viewer
        )

        create_data: Dict[str, Union[str, int]] = {
            "goal": goal.id,
            "text": "New comment",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_comment = GoalComment.objects.filter(
            user=user, goal=goal, text=create_data["text"]
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["goal"][0] == "Вы не можете оставлять комментарии"
        ), "Вы можете создать комментарий"
        assert not unexpected_comment, "Комментарий создан"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_create_archived_goal(self, authenticated_user, user) -> None:
        """
        Test to check if a new comment cannot be created in the archived goal

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 400
            - Unexpected comment does not exist in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        board = BoardFactory()
        category = GoalCategoryFactory(board=board)
        goal = GoalFactory(category=category, status=Goal.Status.archived)
        BoardParticipantFactory(board=board, user=user)

        create_data: Dict[str, Union[str, int]] = {
            "goal": goal.id,
            "text": "New comment",
        }

        response: Response = authenticated_user.post(self.url, data=create_data)
        unexpected_comment = GoalComment.objects.filter(
            user=user, goal=goal, text=create_data["text"]
        ).exists()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Отказ в доступе не предоставлен"
        assert (
            response.data["goal"][0] == "Цель удалена"
        ), "Вы можете создать комментарий"
        assert not unexpected_comment, "Комментарий создан"

    # ----------------------------------------------------------------
    @pytest.mark.django_db
    def test_comment_create_deny(self, api_client) -> None:
        """
        Test that unauthenticated users cannot access the comment create API endpoint

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
