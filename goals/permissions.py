from rest_framework import permissions

from goals.models.board import BoardParticipant
from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory
from goals.models.goal_comment import GoalComment


# ----------------------------------------------------------------------------------------------------------------------
# Create permissions
class BoardPermission(permissions.BasePermission):
    """
    Permission class for Board model,
    determines if a user has permission to access a board
    """

    def has_object_permission(self, request, view, board) -> bool:
        """
        Checks if a user has permission to access a board
        Returns:
            - True if the user has permission to access the board, False otherwise
        """
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user,
                board=board
            ).exists()

        return BoardParticipant.objects.filter(
            user=request.user,
            board=board,
            role=BoardParticipant.Role.owner
        ).exists()


# ----------------------------------------------------------------
class GoalCategoryPermission(permissions.BasePermission):
    """
    Permission class for Category model,
    determines if a user has permission to access a category
    """

    def has_object_permission(self, request, view, category) -> bool:
        """
        Checks if a user has permission to access a category
        Returns:
            - True if the user has permission to access the category, False otherwise
        """
        if request.method in permissions.SAFE_METHODS:
            return GoalCategory.objects.filter(
                board__participants__user=request.user,
                board=category.board
            ).exists()

        return GoalCategory.objects.filter(
            board__participants__user=request.user,
            board=category.board,
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator]
        ).exists()


# ----------------------------------------------------------------
class GoalPermission(permissions.BasePermission):
    """
    Permission class for Goal model,
    determines if a user has permission to access a goal
    """

    def has_object_permission(self, request, view, goal) -> bool:
        """
        Checks if a user has permission to access a goal
        Returns:
            - True if the user has permission to access the goal, False otherwise
        """
        if request.method in permissions.SAFE_METHODS:
            return Goal.objects.filter(
                category__board__participants__user=request.user,
                category__board=goal.category.board
            ).exists()

        return Goal.objects.filter(
            category__board__participants__user=request.user,
            category__board=goal.category.board,
            category__board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator]
        ).exists()


# ----------------------------------------------------------------
class GoalCommentPermission(permissions.BasePermission):
    """
    Permission class for Comment model,
    determines if a user has permission to access a comment
    """

    def has_object_permission(self, request, view, comment) -> bool:
        """
        Checks if a user has permission to access a comment
        Returns:
            - True if the user has permission to access the comment, False otherwise
        """
        if request.method in permissions.SAFE_METHODS:
            return GoalComment.objects.filter(
                goal__category__board__participants__user=request.user,
                goal__category__board=comment.category.board,
            ).exists()

        return GoalComment.objects.filter(
            goal__category__board__participants__user=request.user,
            goal__category__board=comment.goal.category.board,
            goal__category__board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.moderator]
        ).exists()
