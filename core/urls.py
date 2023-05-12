from typing import List

from django.urls import path

from core import views

# ----------------------------------------------------------------------------------------------------------------------
# Create Core app urls
urlpatterns: List = [
    path("signup", views.UserSignupView.as_view(), name="signup"),
    path("login", views.UserLoginView.as_view(), name="login"),
    path("profile", views.UserRetrieveUpdateDestroyView.as_view(), name="profile"),
    path(
        "update_password",
        views.UserPasswordUpdateView.as_view(),
        name="update_password",
    ),
]
