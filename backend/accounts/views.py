from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle, UserRateThrottle
from django.contrib.auth import get_user_model
from . import serializers
from django.contrib.auth import login, logout
from config.utils import format_response


class IsAnonymousUser(BasePermission):
    def has_permission(self, request, view):
        return not bool(request.user and request.user.is_authenticated)


class ResetPasswordConfirmationThrottle(UserRateThrottle):
    scope = 'reset_password_confirmation_throttle'

class SendEmailConfirmationThrottle(UserRateThrottle):
    scope = 'email_confirmation'


class AuthViewSet(GenericViewSet):
    queryset = get_user_model().objects.all()
    throttle_classes = [AnonRateThrottle]

    def get_serializer_class(self):
        if self.action == 'signup':
            return serializers.UserCreationSerializer

        if self.action == 'login':
            return serializers.AuthenticationSerializer

        if self.action == 'email_confirmation':
            return serializers.EmailConfirmationSerializer

        if self.action == 'resend_email_confirmation':
            return serializers.ResendEmailConfirmationSerializer

        if self.action == 'send_reset_password_email_confirmation':
            return serializers.SendResetPasswordEmailConfirmationSerializer

        if self.action == 'confirm_reset_password':
            return serializers.ConfirmResetPasswordSerializer



    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def signup(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            format_response(success=True, message='جهت فعال سازی حساب کاربری ایمیلی به شما ارسال شد.'),
            status=status.HTTP_201_CREATED
        )


    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)

        return Response(
            format_response(success=True, message='ورود با موفقیت انجام شد.'),
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response(
            format_response(success=True, message='خروج با موفقیت انجام شد.'),
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser])
    def email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user.is_active = True
        user.last_login = timezone.now()
        user.save()

        return Response(
            format_response(success=True, message='ایمیل تایید شد.'),
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False, permission_classes=[IsAnonymousUser],
            throttle_classes=[SendEmailConfirmationThrottle])
    def resend_email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            format_response(success=True, message='جهت فعال سازی حساب کاربری ایمیلی به شما ارسال شد.'),
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False,
            throttle_classes=[SendEmailConfirmationThrottle]
            )
    def send_reset_password_email_confirmation(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            format_response(success=True, message='جهت بازنشانی گذرواژه ایمیلی به شما ارسال شد.'),
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False,
            throttle_classes=[ResetPasswordConfirmationThrottle]
            )
    def confirm_reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            format_response(success=True, message='بازنشانی گذرواژه باموفقیت انجام شد.'),
            status=status.HTTP_200_OK
        )