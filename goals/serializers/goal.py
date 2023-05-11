from typing import Tuple

from rest_framework import serializers

from core.serializers import UserRetrieveUpdateSerializer
from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class GoalCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new goal"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields: Tuple[str, ...] = ('id', 'user', 'created', 'updated')

    def validate_category(self, category: GoalCategory) -> GoalCategory:
        """Validate if the category is not deleted and the user has permissions to create a goal"""
        if category.is_deleted:
            raise serializers.ValidationError('Категория удалена')

        if not BoardParticipant.objects.filter(
                board=category.board,
                user=self.context['request'].user,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator],
        ).exists():
            raise serializers.ValidationError('Вы не можете создавать цели')

        return category


# ----------------------------------------------------------------
class GoalSerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating/deleting goal"""
    user = UserRetrieveUpdateSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.all())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields: Tuple[str, ...] = ('id', 'user', 'created', 'updated')
