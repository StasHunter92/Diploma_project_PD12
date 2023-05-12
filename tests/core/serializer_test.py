import logging
from typing import Dict

import pytest

from core.serializers import (
    UserSignupSerializer,
    UserLoginSerializer,
    UserRetrieveUpdateSerializer,
    UserPasswordUpdateSerializer,
)
from tests.factories import UserFactory

# ----------------------------------------------------------------------------------------------------------------------
# Create logger instance
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------------------------------------
# Create tests
@pytest.mark.django_db
def test_user_signup_serializer(new_user) -> None:
    """
    Test UserSignupSerializer to ensure it creates a new user with valid data
    and returns an error if passwords do not match

    Args:
        new_user: A fixture for a new user

    Checks:
        - User instance created successfully
        - ValidationError raised if passwords do not match

    Returns:
        None

    Raises:
        AssertionError
    """
    # Test creating a new user with valid data
    valid_data: Dict[str, str] = {
        "username": new_user.username,
        "password": new_user.password,
        "password_repeat": new_user.password,
    }

    serializer = UserSignupSerializer(data=valid_data)

    assert serializer.is_valid(), "Пароли должны совпадать"
    created_user = serializer.save()

    assert created_user.username == valid_data["username"], "Username не совпадают"
    assert created_user.check_password(valid_data["password"]), "Пароли не совпадают"

    # Test creating a new user with invalid data
    invalid_data: Dict[str, str] = {
        "username": "test_user_2",
        "password": "test_password_2",
        "password_repeat": "wrong_password",
    }

    serializer = UserSignupSerializer(data=invalid_data)

    assert not serializer.is_valid(), "Повторный пароль не должен совпадать"
    assert serializer.errors["non_field_errors"][0] == "Пароли должны совпадать"


# ----------------------------------------------------------------
@pytest.mark.django_db
def test_user_login_serializer(user) -> None:
    """
    Test UserLoginSerializer to ensure it validates user login credentials

    Args:
        user: A fixture that creates a user instance

    Returns:
        None

    Raises:
        AssertionError
    """
    # Test login a user with valid data
    valid_data: Dict[str, str] = {
        "username": user.username,
        "password": "testp@ssword",
    }

    serializer = UserLoginSerializer(data=valid_data)
    assert serializer.is_valid(), "Ошибка в username"

    # Test login a user with invalid data
    invalid_data: Dict[str, str] = {
        "username": "test_user_2",
        "password": "test_password_2",
    }

    serializer = UserLoginSerializer(data=invalid_data)
    assert not serializer.is_valid(), "Введен существующий username"
    assert serializer.errors["username"][0] == "Указанного пользователя не существует"


# ----------------------------------------------------------------
@pytest.mark.django_db
def test_user_retrieve_update_serializer(user, rf) -> None:
    """
    Test UserRetrieveUpdateSerializer to ensure it retrieves and updates user data

    Args:
        user: A fixture that creates a user instance
        rf: A fixture that creates a request factory instance

    Returns:
        None

    Raises:
        AssertionError
    """
    # Test user can update data
    request = rf.patch("/")
    request.user = user

    valid_data: Dict[str, str] = {"username": "updated_user"}

    serializer = UserRetrieveUpdateSerializer(
        instance=user, data=valid_data, partial=True, context={"request": request}
    )

    assert serializer.is_valid(), "Username совпал с существующим"
    updated_user = serializer.save()
    assert updated_user.username == valid_data["username"], "Username не совпадают"

    # Test that second user has same username as updated user
    request = rf.patch("/")
    request.user = UserFactory()

    invalid_data: Dict[str, str] = {"username": "updated_user"}

    serializer = UserRetrieveUpdateSerializer(
        instance=user, data=invalid_data, partial=True, context={"request": request}
    )

    assert not serializer.is_valid(), "Username не совпал с существующим"
    assert serializer.errors["username"][0] == "Введенное имя занято, попробуйте другое"


# ----------------------------------------------------------------
@pytest.mark.django_db
def test_user_password_update_serializer(user, rf) -> None:
    """
    Test the UserPasswordUpdateSerializer to checks
    that the serializer correctly validate a user's password

    Args:
        user: A fixture that creates a user instance
        rf: A fixture that creates a request factory instance

    Returns:
        None

    Raises:
        AssertionError
    """
    # Test user passwords are correct
    request = rf.put("/")
    request.user = user

    valid_data: Dict[str, str] = {
        "old_password": "testp@ssword",
        "new_password": "testp@ssword2",
    }

    serializer = UserPasswordUpdateSerializer(
        instance=user, data=valid_data, partial=True, context={"request": request}
    )

    assert (
        serializer.is_valid()
    ), "Старый пароль не подошел или новый пароль совпал со старым"

    # Test user old password doesn't match current password
    old_password_test_data: Dict[str, str] = {
        "old_password": "not_testpassword",
        "new_password": "testp@ssword2",
    }

    serializer = UserPasswordUpdateSerializer(
        instance=user,
        data=old_password_test_data,
        partial=False,
        context={"request": request},
    )

    assert not serializer.is_valid(), "Старый пароль введен верно"
    assert serializer.errors["old_password"][0] == "Текущий пароль введен неверно"

    # Test user new password match current password
    new_password_test_data: Dict[str, str] = {
        "old_password": "testp@ssword",
        "new_password": "testp@ssword",
    }

    serializer = UserPasswordUpdateSerializer(
        instance=user,
        data=new_password_test_data,
        partial=False,
        context={"request": request},
    )

    assert not serializer.is_valid(), "Новый пароль отличается от старого"
    assert (
        serializer.errors["new_password"][0]
        == "Новый пароль должен отличаться от старого"
    )
