from typing import Tuple

from rest_framework import serializers

from core.serializers import UserRetrieveUpdateSerializer
from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_comment import GoalComment


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new comment"""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields: Tuple[str, ...] = ("id", "user", "created", "updated")

    def validate_goal(self, goal: Goal) -> Goal:
        """Validate if the goal is not deleted and the user has permissions to create a comment"""
        if goal.status == Goal.Status.archived:
            raise serializers.ValidationError("Цель удалена")

        if not BoardParticipant.objects.filter(
            board=goal.category.board,
            user=self.context["request"].user,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator],
        ).exists():
            raise serializers.ValidationError("Вы не можете оставлять комментарии")

        return goal


# ----------------------------------------------------------------
class GoalCommentSerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating/deleting comment"""

    user = UserRetrieveUpdateSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all())

    class Meta:
        model = GoalComment
        fields = "__all__"
        read_only_fields: Tuple[str, ...] = ("id", "user", "created", "updated", "goal")
