from django.urls import path

from core import views

# ----------------------------------------------------------------------------------------------------------------------
# Create user urls
urlpatterns: list = [
    path('signup', views.UserSignupView.as_view(), name='user-signup'),
    path('login', views.UserLoginView.as_view(), name='user-login'),
    path('profile', views.UserRetrieveUpdateView.as_view(), name='user-profile'),
    path('update_password', views.UserPasswordUpdateView.as_view(), name='user-password'),
]
