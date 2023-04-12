from django.db import transaction
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


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    serializer_class = GoalCategoryCreateSerializer
    permission_classes = [IsAuthenticated]


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    @atomic
    def perform_destroy(self, category: GoalCategory):
        # with transaction.atomic():
        category.is_deleted = True
        category.save()
        goals = Goal.objects.filter(user=self.request.user, category=category)
        for goal in goals:
            goal.status = Goal.Status.archived
            goal.save()
        return category


# ----------------------------------------------------------------
class GoalCreateView(CreateAPIView):
    model = Goal
    serializer_class = GoalCreateSerializer
    permission_classes = [IsAuthenticated]


class GoalListView(ListAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_class = GoalDateFilter
    ordering_fields = ['priority', 'due_date']
    # ordering_param = ['priority', 'due_date']
    ordering = ['-priority', 'due_date']
    search_fields = ['title']

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)

    def perform_destroy(self, goal: Goal):
        goal.status = Goal.Status.archived
        goal.save()
        comments = GoalComment.objects.filter(user=self.request.user, goal=goal)
        for comment in comments:
            comment.delete()
        return goal


# ----------------------------------------------------------------
class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [IsAuthenticated]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created', 'updated']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user, goal=self.request.query_params.get('goal'))


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    serializer_class = GoalCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
