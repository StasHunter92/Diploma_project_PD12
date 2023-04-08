from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# User serializers
class UserSignupSerializer(serializers.ModelSerializer):
    """
    Signup serializer for CreateAPIView
    """
    # username = serializers.CharField(max_length=150)
    # first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    # last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    # email = serializers.EmailField(max_length=254, required=False, allow_blank=True)
    password = serializers.CharField(validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    class Meta:
        model: User = User
        fields: list[str] = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'password_repeat']
        read_only_fields: list[str] = ['id']

    # def is_valid(self, raise_exception=False) -> bool:
    #     """
    #     Save and remove repeated password from initial data
    #     :return: True if data is valid
    #     """
    #     # self._password_repeat = self.initial_data.pop('password_repeat')
    #     return super().is_valid(raise_exception=raise_exception)

    # def validate_username(self, username: str) -> str | serializers.ValidationError:
    #     """
    #     Check username doesn't exist in the database
    #     :param username: Username to check
    #     :return: Username or serializers.ValidationError
    #     """
    #     if self.Meta.model.objects.filter(username=username).exists():
    #         raise serializers.ValidationError('Username is already exists')
    #     return username

    def validate(self, validated_data: dict) -> dict | serializers.ValidationError:
        """
        Check passwords match and delete password_repeat from validated_data
        :param validated_data: validated data
        :return: Cleaned validated_data
        """
        """Check passwords match"""
        # if data.get('password') != self._password_repeat:
        if validated_data.get('password') != validated_data.pop('password_repeat'):
            raise serializers.ValidationError('Пароли должны совпадать')
        return validated_data

    def create(self, validated_data: dict) -> User:
        """Create user"""
        user: User = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_username(self, username: str) -> str:
        """Check username doesn't exist in the database"""
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Такого пользователя не существует')
        return username


class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)

    def validate_username(self, value):
        """Check username doesn't exist in the database"""
        # get current user
        current_user = self.context['request'].user

        # check username doesn't exist if it isn't current user
        if self.Meta.model.objects.filter(username=value).exists() and current_user.username != value:
            raise serializers.ValidationError(['User with such username already exists'])
        return value

    class Meta:
        model: User = User
        fields: list[str] = ['username', 'first_name', 'last_name', 'email']
        read_only_fields: list[str] = ['id']


class UserPasswordUpdateSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, validators=[validate_password])
    new_password = serializers.CharField(required=True, validators=[validate_password])

    # def validate_new_password(self, value):
    #     validate_password(value)
    #     return
