from django.urls import path

from bot import views

# ----------------------------------------------------------------------------------------------------------------------
# Create bot urls
urlpatterns: list = [
    path('verify', views.TelegramUserVerificationView.as_view(), name='verify'),
]