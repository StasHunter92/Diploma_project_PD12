import django_filters
from django.db import models
from django_filters import rest_framework

from goals.models.goal import Goal


# ----------------------------------------------------------------------------------------------------------------------
# Create filters
class GoalDateFilter(rest_framework.FilterSet):
    """A filter for the Goal model that allows filtering by due_date, category, status, and priority"""

    class Meta:
        model = Goal
        fields = {
            "due_date": ("lte", "gte"),
            "category": ("exact", "in"),
            "status": ("exact", "in"),
            "priority": ("exact", "in"),
        }

    filter_overrides = {
        models.DateTimeField: {"filter_class": django_filters.IsoDateTimeFilter},
    }
