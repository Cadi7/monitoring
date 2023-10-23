from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from drf_util.decorators import serialize_decorator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User
from apps.users.permissions import IsOwner
from apps.users.serializers import RegisterSerializer, LoginSerializer
from config.settings import EMAIL_HOST_USER, WEB_HOST


class UserViewSet(GenericViewSet):
    serializer_class = RegisterSerializer
    queryset = User.objects.all().order_by('id')
    permission_classes = [IsOwner]

    @serialize_decorator(RegisterSerializer)
    @action(methods=['post'], detail=False, serializer_class=RegisterSerializer, permission_classes=[AllowAny])
    def register(self, request):
        user = User.objects.create(
            first_name=request.valid['first_name'],
            last_name=request.valid['last_name'],
            username=request.valid['email'],
            email=request.valid['email'],
        )
        user.set_password(request.valid['password'])
        user.save()

        confirmation_token = default_token_generator.make_token(user)
        activation_link = WEB_HOST + f'users/activate?user_id={user.id}&confirmation_token={confirmation_token}'

        html_content = render_to_string('email.html', {
            'activation_link': activation_link,
            'first_name': user.first_name
        })
        send_mail("Confirm email", activation_link, EMAIL_HOST_USER, [user.email], html_message=html_content)

        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=[AllowAny])
    def activate(self, request, pk=None):
        user_id = request.query_params.get('user_id', '')
        confirmation_token = request.query_params.get('confirmation_token', '')
        user = get_object_or_404(self.get_queryset(), pk=user_id)

        if not default_token_generator.check_token(user, confirmation_token):
            raise "Invalid token"

        user.is_active = True
        user.is_confirmed = True
        user.save()

        return Response('Email successfully confirmed', status=status.HTTP_200_OK)

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @action(detail=False, permission_classes=[AllowAny], methods=['post'], url_path='login',
            serializer_class=LoginSerializer)
    def login(self, request):
        user = get_object_or_404(User, email=request.data['email'])
        if not user.is_confirmed:
            raise AuthenticationFailed('User is not confirmed')
        return Response(self.get_tokens_for_user(user), status=status.HTTP_200_OK)
