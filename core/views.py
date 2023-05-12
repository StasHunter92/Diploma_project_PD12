from typing import Any

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.serializers import UserSignupSerializer, \
    UserLoginSerializer, UserRetrieveUpdateSerializer, \
    UserPasswordUpdateSerializer


# ----------------------------------------------------------------------------------------------------------------------
# User views
class UserSignupView(CreateAPIView):
    """Create a new user"""

    queryset = User.objects.all()
    serializer_class = UserSignupSerializer


# ----------------------------------------------------------------
class UserLoginView(CreateAPIView):
    """Login user"""

    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Method to check input user data and login user

        Returns:
            Success response or Failure response with error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username: str = serializer.validated_data["username"]
        password: str = serializer.validated_data["password"]
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response(status=status.HTTP_201_CREATED)

        raise AuthenticationFailed("Неверные учетные данные")


# ----------------------------------------------------------------
class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """View for retrieving user information, updating or logout user"""

    serializer_class = UserRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Any:
        return self.request.user

    def delete(self, request: Request, *args, **kwargs) -> Response:
        """
        Logout user from application

        Returns:
            204 No content response
        """
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------------------
class UserPasswordUpdateView(UpdateAPIView):
    """View for updating user password"""

    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Any:
        return self.request.user

    def put(self, request: Request, *args, **kwargs) -> Response:
        """
        Method to check input user data and change password

        Returns:
            Success response 200 or Failure response 404
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = self.get_object()
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response(status=status.HTTP_200_OK)
