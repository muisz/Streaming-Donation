from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt import authentication

from apps.user.api.serializers import (
    AuthUserSerializer,
    LoginUserSerializer,
    RegisterUserSerializer,
)


class AuthView(GenericViewSet):
    permission_classes = ()
    authentication_classes = ()
    
    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = RegisterUserSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_serializer = AuthUserSerializer(user, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = LoginUserSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()
        user.update_last_login()

        response_serializer = AuthUserSerializer(user, context=self.get_serializer_context())
        return Response(response_serializer.data)
    
    @action(
        methods=['post'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        authentication_classes=(authentication.JWTAuthentication,)
    )
    def logout(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


auth_view = AuthView
