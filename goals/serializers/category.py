from typing import Tuple

from rest_framework import serializers

from core.serializers import UserRetrieveUpdateSerializer
from goals.models.board import BoardParticipant, Board
from goals.models.goal_category import GoalCategory


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new category"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields: Tuple[str, ...] = ('id', 'user', 'created', 'updated')

    def validate_board(self, board: Board) -> Board:
        """Validate if the board is not deleted and the user has permissions to create a category"""
        if board.is_deleted:
            raise serializers.ValidationError('Доска удалена')

        if not BoardParticipant.objects.filter(
                board=board,
                user=self.context['request'].user,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator]
        ).exists():
            raise serializers.ValidationError('Вы не можете создавать категории')

        return board


# ----------------------------------------------------------------
class GoalCategorySerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating/deleting category"""
    user = UserRetrieveUpdateSerializer(read_only=True)
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields: Tuple[str, ...] = ('id', 'user', 'created', 'updated', 'board')
