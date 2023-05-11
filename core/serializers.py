from typing import Dict, Tuple

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# User serializers
class UserSignupSerializer(serializers.ModelSerializer):
    """
    Signup serializer for CreateAPIView
    Handles user registration with password validation and hashing
    """
    password = serializers.CharField(validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields: Tuple[str, ...] = ('id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat')
        read_only_fields: Tuple[str, ...] = ('id',)

    def validate(self, validated_data: Dict) -> Dict:
        """
        Checks that 'password' and 'password_repeat' match
        and remove 'password_repeat' from 'validated_data'

        Args:
            validated_data: The validated data from the serializer

        Returns:
            The cleaned validated data

        Raises:
            serializers.ValidationError: If 'password' and 'password_repeat' do not match
        """
        if validated_data.get('password') != validated_data.pop('password_repeat'):
            raise serializers.ValidationError('Пароли должны совпадать')

        return validated_data

    def create(self, validated_data: Dict) -> User:
        """
        Creates a new user with hashed password

        Args:
            validated_data: The validated data from the serializer

        Returns:
            User: The newly created user instance
        """
        new_user: User = User.objects.create(**validated_data)
        new_user.set_password(validated_data['password'])
        new_user.save()

        return new_user


# ----------------------------------------------------------------
class UserLoginSerializer(serializers.Serializer):
    """
    Login serializer for CreateAPIView
    Handles user authentication by checking if the provided username exists in the database
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_username(self, username: str) -> str:
        """
        Checks that given username exists in the database

        Args:
            username: The username to check

        Returns:
            str: The given username, if it exists in the database

        Raises:
            serializers.ValidationError: If the given username does not exist in the database
        """
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Указанного пользователя не существует')

        return username


# ----------------------------------------------------------------
class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for RetrieveUpdateDestroyAPIView
    Handles user profile retrieval and updates, ensuring that the updated username is unique
    """
    username = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields: Tuple[str, ...] = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields: Tuple[str, ...] = ('id',)

    def validate_username(self, username: str) -> str:
        """
        Checks if the given username is unique, excluding the current user

        Args:
            username: The username to check

        Returns:
            str: The given username, if it is unique

        Raises:
            serializers.ValidationError: If the given username already exists in the database
                and belongs to a different user
        """
        current_user: User = self.context['request'].user

        if User.objects.filter(username=username).exists() and current_user.username != username:
            raise serializers.ValidationError('Введенное имя занято, попробуйте другое')

        return username


# ----------------------------------------------------------------
class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for UpdateAPIView
    Handles user password updates, ensuring that the old password is correct and the new password is different
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model = User
        fields: Tuple[str, ...] = ('old_password', 'new_password')

    def validate_old_password(self, old_password: str) -> str:
        """
        Validates that the old password provided matches the user's current password

        Args:
            old_password: The user's old password

        Returns:
            str: The old password if it is correct

        Raises:
            serializers.ValidationError: If the old password does not match the user's current password
        """
        current_user: User = self.context['request'].user

        if not current_user.check_password(old_password):
            raise serializers.ValidationError('Текущий пароль введен неверно')

        return old_password

    def validate_new_password(self, new_password: str) -> str:
        """
        Validates that the new password is different from the user's current password

        Args:
            new_password: The user's new password

        Returns:
            str: The new password if it is different from the user's current password

        Raises:
            serializers.ValidationError: If the new password is the same as the user's current password
        """
        current_user: User = self.context['request'].user

        if current_user.check_password(new_password):
            raise serializers.ValidationError('Новый пароль должен отличаться от старого')

        return new_password
