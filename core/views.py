from django.contrib.auth import authenticate, login, logout

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import User
from core.serializers import UserSignupSerializer, UserLoginSerializer, UserRetrieveUpdateSerializer, \
    UserPasswordUpdateSerializer


# ----------------------------------------------------------------------------------------------------------------------
# User views
class UserSignupView(CreateAPIView):
    """
    Create new user
    """
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer


class UserLoginView(CreateAPIView):
    """
    Login user
    """
    serializer_class = UserLoginSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Check input user data and login user
        :return: Success response or Failure response with error
        """
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username: str = request.data.get('username')
        password: str = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return Response(status=status.HTTP_201_CREATED)

        raise AuthenticationFailed('Неверные учетные данные.')


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving user information, updating or logout user
    """
    model = User
    serializer_class = UserRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    def delete(self, request: Request, *args, **kwargs) -> Response:
        """
        Logout user from application
        :return: No content response
        """
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPasswordUpdateView(UpdateAPIView):
    """
    View for updating user password
    """
    model = User
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> User:
        return self.request.user

    def put(self, request: Request, *args, **kwargs) -> Response:
        """
        Check input user data and change password
        :return: Success response or Failure response with error
        """
        serializer = self.get_serializer(data=request.data)
        user: User = self.get_object()

        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        return Response(status=status.HTTP_200_OK)
