from django.db.models import QuerySet
from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory
from goals.permissions import GoalCategoryPermission
from goals.serializers.category import GoalCategoryCreateSerializer, GoalCategorySerializer


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class GoalCategoryCreateView(CreateAPIView):
    """API endpoint for creating a new category"""
    model = GoalCategory
    serializer_class = GoalCategoryCreateSerializer
    permission_classes: tuple = (IsAuthenticated,)


# ----------------------------------------------------------------
class GoalCategoryListView(ListAPIView):
    """API endpoint for retrieving a list of categories"""
    serializer_class = GoalCategorySerializer
    permission_classes: tuple = (IsAuthenticated, GoalCategoryPermission)
    pagination_class = LimitOffsetPagination

    filter_backends: tuple = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields: tuple[str, ...] = ('title', 'created')
    ordering: tuple[str] = ('title',)
    search_fields: tuple[str] = ('title',)
    filterset_fields: tuple[str] = ('board',)

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """Return a queryset of categories the user is a participant of"""
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False)


# ----------------------------------------------------------------
class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving/updating/deleting a category"""
    serializer_class = GoalCategorySerializer
    permission_classes: tuple = (IsAuthenticated, GoalCategoryPermission)

    def get_queryset(self) -> QuerySet[GoalCategory]:
        """Return a queryset of categories the user is a participant of"""
        return GoalCategory.objects.select_related('board').filter(
            board__participants__user=self.request.user,
            board__is_deleted=False,
            is_deleted=False)

    @atomic
    def perform_destroy(self, category: GoalCategory) -> None:
        """Delete a category and archive all of its goals"""
        category.is_deleted = True
        category.save(update_fields=('is_deleted',))
        category.goals.update(status=Goal.Status.archived)
        # return category
