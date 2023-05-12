from typing import List

from django.urls import path

from bot import views

# ----------------------------------------------------------------------------------------------------------------------
# Create Bot app urls
urlpatterns: List = [
    path("verify", views.TelegramUserVerificationView.as_view(), name="verify"),
]
