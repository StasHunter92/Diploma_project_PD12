from rest_framework import serializers

from core.serializers import UserRetrieveUpdateSerializer
from goals.models import GoalCategory, Goal, GoalComment


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Create a serializer for GoalCategory"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')


class GoalCategorySerializer(serializers.ModelSerializer):
    """RetrieveUpdateDestroy serializer for GoalCategory"""
    user = UserRetrieveUpdateSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')


# ----------------------------------------------------------------
class GoalCreateSerializer(serializers.ModelSerializer):
    """Create a serializer for Goal"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def validate_category(self, category: GoalCategory) -> GoalCategory:
        """Check the category deleted status or if the user is not the owner of this category"""
        if category.is_deleted:
            raise serializers.ValidationError("Категория удалена")
        if category.user != self.context['request'].user:
            raise serializers.ValidationError('У Вас нет доступа к этой категории')
        return category


class GoalSerializer(serializers.ModelSerializer):
    """RetrieveUpdateDestroy serializer for Goal"""
    user = UserRetrieveUpdateSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')


# ----------------------------------------------------------------
class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Create a serializer for GoalComment"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def validate_goal(self, goal: Goal) -> Goal:
        """Check the goal archived status or if the user is not the owner of this goal"""
        if goal.status == Goal.Status.archived:
            raise serializers.ValidationError("Цель удалена")
        if goal.user != self.context['request'].user:
            raise serializers.ValidationError('У Вас нет доступа к этой цели')
        return goal


class GoalCommentSerializer(serializers.ModelSerializer):
    """RetrieveUpdateDestroy serializer for GoalComment"""
    user = UserRetrieveUpdateSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated', 'goal')
