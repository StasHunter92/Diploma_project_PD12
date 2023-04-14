from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.filters import GoalDateFilter
from goals.models import GoalCategory, Goal, GoalComment
from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, \
    GoalSerializer, GoalCommentSerializer, GoalCommentCreateSerializer


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class GoalCategoryCreateView(CreateAPIView):
    """Create category"""
    model = GoalCategory
    serializer_class = GoalCategoryCreateSerializer
    permission_classes: list = [IsAuthenticated]


class GoalCategoryListView(ListAPIView):
    """Get list of categories"""
    serializer_class = GoalCategorySerializer
    permission_classes: list = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    filter_backends: list = [OrderingFilter, SearchFilter]
    ordering_fields: list[str] = ['title', 'created']
    ordering: list[str] = ['title']
    search_fields: list[str] = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """Get, update or delete a category"""
    serializer_class = GoalCategorySerializer
    permission_classes: list = [IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    @atomic
    def perform_destroy(self, category: GoalCategory) -> GoalCategory:
        """Marks the category as deleted and changes the status of its goals to "archived"""
        category.is_deleted = True
        category.save(update_fields=('is_deleted',))
        goals = Goal.objects.filter(user=self.request.user, category=category)
        goals.update(status=Goal.Status.archived)
        return category


# ----------------------------------------------------------------
class GoalCreateView(CreateAPIView):
    """Create goal"""
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes: list = [IsAuthenticated]


class GoalListView(ListAPIView):
    """Get list of goals"""
    serializer_class = GoalSerializer
    permission_classes: list = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    filter_backends: list = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields: list = ['priority', 'due_date']
    ordering: list = ['-priority', 'due_date']
    search_fields: list = ['title']
    filterset_class = GoalDateFilter

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    """Get, update or delete a goal"""
    serializer_class = GoalSerializer
    permission_classes: list = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)

    @atomic()
    def perform_destroy(self, goal: Goal) -> Goal:
        """Changes the status of the goal to 'archived' and deletes comments"""
        goal.status = Goal.Status.archived
        goal.save(update_fields=('status',))
        comments = GoalComment.objects.filter(user=self.request.user, goal=goal)
        comments.delete()
        return goal


# ----------------------------------------------------------------
class GoalCommentCreateView(CreateAPIView):
    """Create comment"""
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes: list = [IsAuthenticated]


class GoalCommentListView(ListAPIView):
    """Get list of comments"""
    serializer_class = GoalCommentSerializer
    permission_classes: list = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    filter_backends: list = [OrderingFilter, DjangoFilterBackend]
    ordering_fields: list = ['created', 'updated']
    ordering: list = ['-created']
    filterset_fields = ['goal']

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user).select_related('user')


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """Get, update or delete a comment"""
    serializer_class = GoalCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
