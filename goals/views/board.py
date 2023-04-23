from django.db.models import QuerySet
from django.db.transaction import atomic

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.models.board import Board
from goals.models.goal import Goal
from goals.permissions import BoardPermission
from goals.serializers.board import BoardCreateSerializer, BoardListSerializer, BoardSerializer


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class BoardCreateView(CreateAPIView):
    """API endpoint for creating a new board"""
    model = Board
    serializer_class = BoardCreateSerializer
    permission_classes: tuple = (IsAuthenticated,)


# ----------------------------------------------------------------
class BoardListView(ListAPIView):
    """API endpoint for retrieving a list of boards"""
    serializer_class = BoardListSerializer
    permission_classes: tuple = (IsAuthenticated, BoardPermission)
    pagination_class = LimitOffsetPagination

    ordering: tuple[str] = ('title',)

    def get_queryset(self) -> QuerySet[Board]:
        """Return a queryset of boards the user is a participant of"""
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)


# ----------------------------------------------------------------
class BoardView(RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving/updating/deleting a board"""
    serializer_class = BoardSerializer
    permission_classes: tuple = (IsAuthenticated, BoardPermission)

    def get_queryset(self) -> QuerySet[Board]:
        """Return a queryset of boards the user is a participant of"""
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    @atomic()
    def perform_destroy(self, board: Board) -> Board:
        """Delete a board with all categories and archive all of its goals"""
        board.is_deleted = True
        board.save(update_fields=('is_deleted',))
        board.categories.update(is_deleted=True)
        Goal.objects.filter(category__board=board).update(status=Goal.Status.archived)
        return board
