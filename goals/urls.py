from typing import List

from django.urls import path

from goals.views import board, category, goal, comment

# ----------------------------------------------------------------------------------------------------------------------
# Create Goal app urls
urlpatterns: List = [
    # Board urls
    path("board/create", board.BoardCreateView.as_view(), name="board_create"),
    path("board/list", board.BoardListView.as_view(), name="board_list"),
    path("board/<int:pk>", board.BoardView.as_view(), name="board"),
    # Category urls
    path(
        "goal_category/create",
        category.GoalCategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "goal_category/list",
        category.GoalCategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "goal_category/<int:pk>", category.GoalCategoryView.as_view(), name="category"
    ),
    # Goal urls
    path("goal/create", goal.GoalCreateView.as_view(), name="goal_create"),
    path("goal/list", goal.GoalListView.as_view(), name="goal_list"),
    path("goal/<int:pk>", goal.GoalView.as_view(), name="goal"),
    # Comment urls
    path(
        "goal_comment/create",
        comment.GoalCommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        "goal_comment/list", comment.GoalCommentListView.as_view(), name="comment_list"
    ),
    path("goal_comment/<int:pk>", comment.GoalCommentView.as_view(), name="comment"),
]
