from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

# ----------------------------------------------------------------------------------------------------------------------
# Get user model from project
User = get_user_model()


# ----------------------------------------------------------------------------------------------------------------------
# User serializers
class UserSignupSerializer(serializers.ModelSerializer):
    """
    Signup serializer for CreateAPIView
    """
    password = serializers.CharField(validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model: User = User
        fields: list[str] = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']
        read_only_fields: list[str] = ['id']

    def validate(self, validated_data: dict) -> dict | serializers.ValidationError:
        """
        Check passwords match and delete password_repeat from validated_data
        :param validated_data: Validated data
        :return: Cleaned validated_data or ValidationError
        """
        if validated_data.get('password') != validated_data.pop('password_repeat'):
            raise serializers.ValidationError('Пароли должны совпадать.')
        return validated_data

    def create(self, validated_data: dict) -> User:
        """
        Create user and hash password
        :param validated_data: Validated data
        :return: User instance
        """
        user: User = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Login serializer for CreateAPIView
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_username(self, username: str) -> str | serializers.ValidationError:
        """
        Check username doesn't exist in the database
        :param username: Username to check
        :return: Username or ValidationError
        """
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Такого пользователя не существует.')
        return username


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for RetrieveUpdateDestroyAPIView
    """
    username = serializers.CharField(max_length=150, required=False)

    def validate_username(self, username: str) -> str | serializers.ValidationError:
        """
        Check username doesn't exist in the database
        :param username: Username to check
        :return: Username or ValidationError
        """
        current_user = self.context['request'].user

        if self.Meta.model.objects.filter(username=username).exists() and current_user.username != username:
            raise serializers.ValidationError('Пользователь с таким именем уже существует.')
        return username

    class Meta:
        model: User = User
        fields: list[str] = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields: list[str] = ['id']


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for UpdateAPIView
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model: User = User
        fields: list[str] = ['old_password', 'new_password']

    def validate_old_password(self, old_password: str) -> str | serializers.ValidationError:
        """
        Check old password is correct
        :param old_password: User old password
        :return: Password or ValidationError
        """
        current_user: User = self.context['request'].user
        if not current_user.check_password(old_password):
            raise serializers.ValidationError('Неправильный пароль.')
        return old_password

    def validate_new_password(self, new_password: str) -> str | serializers.ValidationError:
        """
        Check new password is not same as old password
        :param new_password: User new password
        :return: Password or ValidationError
        """
        current_user: User = self.context['request'].user
        if current_user.check_password(new_password):
            raise serializers.ValidationError('Новый пароль должен отличаться от старого.')
        return new_password
