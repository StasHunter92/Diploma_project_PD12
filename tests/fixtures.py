import datetime
import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory


# ----------------------------------------------------------------------------------------------------------------------
# Create fixtures
@pytest.fixture
def api_client() -> APIClient:
    """A fixture that creates an instance of the APIClient"""
    return APIClient()


@pytest.fixture
def user():
    """A fixture that creates a user instance"""
    return UserFactory.create(username="username", password="testp@ssword")


@pytest.fixture
def authenticated_user(api_client, user) -> APIClient:
    """A fixture that creates authenticated user on the APIClient"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def new_user():
    """A fixture that builds a user instance without database"""
    return UserFactory.build()


@pytest.fixture
def due_date():
    """A fixture that creates a date with the timedelta from the current date"""
    due_date: datetime = datetime.date.today() + datetime.timedelta(days=7)
    return due_date.strftime("%Y-%m-%d")
