from django.urls import path

from goals.views import board, category, goal, comment

urlpatterns = [
    # Board urls
    path('board/create', board.BoardCreateView.as_view()),
    path('board/list', board.BoardListView.as_view()),
    path('board/<int:pk>', board.BoardView.as_view()),

    # Category urls
    path('goal_category/create', category.GoalCategoryCreateView.as_view()),
    path('goal_category/list', category.GoalCategoryListView.as_view()),
    path('goal_category/<int:pk>', category.GoalCategoryView.as_view()),

    # Goal urls
    path('goal/create', goal.GoalCreateView.as_view()),
    path('goal/list', goal.GoalListView.as_view()),
    path('goal/<int:pk>', goal.GoalView.as_view()),

    # Comment urls
    path('goal_comment/create', comment.GoalCommentCreateView.as_view()),
    path('goal_comment/list', comment.GoalCommentListView.as_view()),
    path('goal_comment/<int:pk>', comment.GoalCommentView.as_view()),
]
