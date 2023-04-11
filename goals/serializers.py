from rest_framework import serializers

from core.serializers import UserRetrieveUpdateSerializer
from goals.models import GoalCategory, Goal


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created', 'updated']


class GoalCategorySerializer(serializers.ModelSerializer):
    user = UserRetrieveUpdateSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created', 'updated']


# ----------------------------------------------------------------
class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.all())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created', 'updated']

    def validate_category(self, category):
        if category.is_deleted:
            raise serializers.ValidationError("Категория удалена")
        if category.user != self.context['request'].user:
            raise serializers.ValidationError('У Вас нет доступа к этой категории')
        return category


class GoalSerializer(serializers.ModelSerializer):
    user = UserRetrieveUpdateSerializer(read_only=True)
    category = GoalCategorySerializer

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created', 'updated']
