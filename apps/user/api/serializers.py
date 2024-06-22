from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    def create(self, validated_data):
        return User.register(validated_data.get('name'), validated_data.get('email'), validated_data.get('password'))

    class Meta:
        model = User
        fields = ('name', 'email', 'password')


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    _user = None

    def validate(self, attrs):
        try:
            user = User.authenticate(attrs.get('email'), attrs.get('password'))
            self._user = user
            return attrs

        except Exception as error:
            raise ValidationError(error)
    
    def get_user(self):
        return self._user



class AuthUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return {
            "access": str(token.access_token),
            "refresh": str(token)
        }

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'email',
            'token',
        )
