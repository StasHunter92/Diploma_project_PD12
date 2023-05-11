from django.db.models import QuerySet
from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter
from goals.models.goal import Goal
from goals.permissions import GoalPermission
from goals.serializers.goal import GoalCreateSerializer, GoalSerializer


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class GoalCreateView(CreateAPIView):
    """API endpoint for creating a new goal"""
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes: tuple = (IsAuthenticated,)


# ----------------------------------------------------------------
class GoalListView(ListAPIView):
    """API endpoint for retrieving a list of goals"""
    serializer_class = GoalSerializer
    permission_classes: tuple = (IsAuthenticated, GoalPermission)
    pagination_class = LimitOffsetPagination

    filter_backends: tuple = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields: tuple[str, ...] = ('priority', 'due_date')
    ordering: tuple[str, ...] = ('-priority', 'due_date')
    search_fields: tuple[str] = ('title',)
    filterset_class = GoalDateFilter
    filterset_fields: tuple[str] = ('category',)

    def get_queryset(self) -> QuerySet[Goal]:
        """Return a queryset of goals the user is a participant of"""
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)


# ----------------------------------------------------------------
class GoalView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving/updating/deleting a goal"""
    serializer_class = GoalSerializer
    permission_classes: tuple = (IsAuthenticated, GoalPermission)

    def get_queryset(self) -> QuerySet[Goal]:
        """Return a queryset of goals the user is a participant of"""
        return Goal.objects.select_related('category').filter(
            category__board__participants__user=self.request.user,
            category__board__is_deleted=False,
            category__is_deleted=False
        ).exclude(status=Goal.Status.archived)

    @atomic()
    def perform_destroy(self, goal: Goal) -> None:
        """Archive a goal and delete all of its comments"""
        goal.status = Goal.Status.archived
        goal.save(update_fields=('status',))
        goal.comments.all().delete()
        # return goal
