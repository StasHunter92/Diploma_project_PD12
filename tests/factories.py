import datetime

import factory
from django.contrib.auth import get_user_model

from goals.models.board import Board, BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory
from goals.models.goal_comment import GoalComment

# ----------------------------------------------------------------------------------------------------------------------
# Get user model from project
User = get_user_model()


# ----------------------------------------------------------------------------------------------------------------------
# Create factories
class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating User instances with randomized data

    Returns:
        User instance with randomized data
    """

    username = factory.Faker("user_name")
    password = factory.Faker("password")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User

    @classmethod
    def create(cls, **kwargs):
        custom_password = kwargs.pop("password", None)
        user = super().create(**kwargs)
        if custom_password:
            user.set_password(custom_password)
            user.save()
        else:
            user.set_password(str(cls.password))
            user.save()
        return user


# ----------------------------------------------------------------
class BoardFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Board instances with randomized data

    Returns:
        Board instance with randomized data
    """

    title = factory.Faker("sentence", nb_words=2)

    class Meta:
        model = Board


# ----------------------------------------------------------------
class GoalCategoryFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Category instances with randomized data

    Returns:
        Category instance with randomized data
    """

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=2)

    class Meta:
        model = GoalCategory


# ----------------------------------------------------------------
class GoalFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Goal instances with randomized data

    Returns:
        Goal instance with randomized data
    """

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    title = factory.Faker("sentence", nb_words=2)
    description = factory.Faker("sentence", nb_words=10)
    due_date = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    class Meta:
        model = Goal


# ----------------------------------------------------------------
class GoalCommentFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Comment instances with randomized data

    Returns:
        Comment instance with randomized data
    """

    goal = factory.SubFactory(GoalFactory)
    user = factory.SubFactory(UserFactory)
    text = factory.Faker("sentence", nb_words=10)

    class Meta:
        model = GoalComment


# ----------------------------------------------------------------
class BoardParticipantFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Participant instances with randomized data

    Returns:
        Participant instance with randomized data
    """

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant
