from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.models.goal import Goal
from goals.models.goal_comment import GoalComment
from goals.permissions import GoalCommentPermission
from goals.serializers.comment import GoalCommentCreateSerializer, GoalCommentSerializer


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class GoalCommentCreateView(CreateAPIView):
    """API endpoint for creating a new comment"""

    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes: tuple = (IsAuthenticated,)


# ----------------------------------------------------------------
class GoalCommentListView(ListAPIView):
    """API endpoint for retrieving a list of comments"""

    serializer_class = GoalCommentSerializer
    permission_classes: tuple = (IsAuthenticated, GoalCommentPermission)
    pagination_class = LimitOffsetPagination

    filter_backends: tuple = (OrderingFilter, DjangoFilterBackend)
    ordering_fields: tuple[str, ...] = ("created", "updated")
    ordering: tuple[str] = ("-created",)
    filterset_fields: tuple[str] = ("goal",)

    def get_queryset(self) -> QuerySet[GoalComment]:
        """Return a queryset of comments the user is a participant of"""
        return (
            GoalComment.objects.select_related("goal")
            .filter(
                goal__category__board__participants__user=self.request.user,
                goal__category__board__is_deleted=False,
                goal__category__is_deleted=False,
            )
            .exclude(goal__status=Goal.Status.archived)
        )


# ----------------------------------------------------------------
class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving/updating/deleting a comment"""

    serializer_class = GoalCommentSerializer
    permission_classes: tuple = (IsAuthenticated, GoalCommentPermission)

    def get_queryset(self) -> QuerySet[GoalComment]:
        """Return a queryset of comments the user is a participant of"""
        return (
            GoalComment.objects.select_related("goal")
            .filter(
                goal__category__board__participants__user=self.request.user,
                goal__category__board__is_deleted=False,
                goal__category__is_deleted=False,
            )
            .exclude(goal__status=Goal.Status.archived)
        )
