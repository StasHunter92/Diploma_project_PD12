import logging
from typing import Dict

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

# ----------------------------------------------------------------------------------------------------------------------
# Get user model from project
User = get_user_model()

# ----------------------------------------------------------------------------------------------------------------------
# Create logger instance
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
@pytest.mark.django_db
class TestCoreViews:
    """Tests for core application views"""

    def test_user_signup(self, api_client) -> None:
        """
        Test user signup by making a POST request to the signup URL with user data

        Args:
            api_client: API client for testing

        Checks:
            - Response status code is 201
            - User exists in the database

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("signup")

        signup_data: Dict[str, str] = {
            "username": "new_username",
            "password": "new_testp@ssword",
            "password_repeat": "new_testp@ssword",
        }

        response: Response = api_client.post(url, data=signup_data)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Пользователь не создался"
        assert User.objects.filter(
            username=signup_data["username"]
        ).exists(), "Пользователя не существует"

    # ----------------------------------------------------------------
    def test_user_login(self, api_client, user) -> None:
        """
        Test user login by making a POST request to the login URL with user credentials

        Args:
            api_client: API client for testing
            user: A fixture that creates a user instance

        Checks:
            - Response status code is 201
            - Session exists

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("login")
        login_data: Dict[str, str] = {
            "username": "username",
            "password": "testp@ssword",
        }

        response: Response = api_client.post(url, data=login_data)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), "Пользователь не авторизовался"
        assert "sessionid" in response.cookies, "Сессии нет"

    # ----------------------------------------------------------------
    def test_user_retrieve_update_destroy(
        self, api_client, authenticated_user, user
    ) -> None:
        """
        Test user profile retrieve, update, and destroy requests to the profile URL

        Args:
            api_client: API client for testing
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - User can get profile
            - User can update profile
            - User can log out
            - Unauthenticated user can not get profile

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("profile")

        # Check GET request
        response: Response = authenticated_user.get(url)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert response.data["first_name"] == user.first_name, "Имя не совпадает"
        assert response.data["last_name"] == user.last_name, "Фамилия не совпадает"

        # Check PATCH request
        update_data: Dict[str, str] = {
            "first_name": "Test",
            "last_name": "User",
        }

        response = authenticated_user.patch(url, data=update_data)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert (
            response.data["first_name"] == update_data["first_name"]
        ), "Имя не обновилось"
        assert (
            response.data["last_name"] == update_data["last_name"]
        ), "Фамилия не обновилась"

        # Check DELETE request
        response = authenticated_user.delete(url)

        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), "Пользователь не вышел"

        # Check unauthorized GET request
        api_client.logout()
        response = api_client.get(url)
        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Отказ в доступе не был дан"

    # ----------------------------------------------------------------
    def test_user_password_update(self, authenticated_user, user) -> None:
        """
        Test user password update by making a PUT request to the update password URL with old and new passwords

        Args:
            authenticated_user: API client with authenticated user for testing
            user: A fixture that creates a user instance

        Checks:
            - User can update password

        Returns:
            None

        Raises:
            AssertionError
        """
        url: str = reverse("update_password")

        update_data: Dict[str, str] = {
            "old_password": "testp@ssword",
            "new_password": "newp@ssword22",
        }

        response: Response = authenticated_user.put(url, data=update_data)

        assert response.status_code == status.HTTP_200_OK, "Запрос не прошел"
        assert user.check_password(update_data["new_password"]), "Пароль не обновился"
