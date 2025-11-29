from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, UserAttributeSimilarityValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from accounts.models import CustomUser

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.db.models import Q

USER_MODEL: CustomUser = get_user_model()


def send_confirmation_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user=user)

    subject = "ورود به حساب کاربری"
    from_email = settings.EMAIL_HOST_USER

    html_content = render_to_string("accounts/email_confirmation.html",
                                    {"username": user.username,
                                     'login_url': settings.FRONTEND_EMAIL_CONFIRMATION_URL.format(uid, token)})

    msg = EmailMultiAlternatives(subject, "", from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

class UserCreationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, label='گذرواژه')
    password2 = serializers.CharField(write_only=True, label='تکرار گذرواژه')

    class Meta:
        model = USER_MODEL
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2' )


    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')
        email = data.get('email')
        username = data.get('username')
        if password1 != password2:
            raise serializers.ValidationError({'password':'دو گذرواژه یکسان نیست.'})

        try:
            temp_user = USER_MODEL(username=username, email=email)
            validate_password(password1, user=temp_user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})

        return data



    def create(self, validated_data):
            validated_data.pop('password1')
            password = validated_data.pop('password2')
            user = USER_MODEL.objects.create_user(**validated_data)
            user.set_password(password)
            user.is_active = False
            user.save()

            send_confirmation_email(user)

            return user


class AuthenticationSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(label='نام کاربری یا ایمیل')
    password = serializers.CharField(write_only=True, label='گذرواژه')

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        user = USER_MODEL.objects.filter(Q(email=email_or_username) | Q(username=email_or_username), is_active=True)

        user = user.first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({'detail':'اطلاعات وارد شده معتبر نیست.'})

        return {'user': user}

class EmailConfirmationSerializer(serializers.Serializer):
    token = serializers.CharField()
    user_id = serializers.CharField()

    def validate(self, data):
        token = data.get('token')

        try:
            uid = force_str(urlsafe_base64_decode(data.get("user_id")))
            user = USER_MODEL.objects.get(pk=uid)
        except (USER_MODEL.DoesNotExist , ValueError):
            raise serializers.ValidationError({'detail': 'تایید ایمیل ناموفق'})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({'detail': 'تایید ایمیل ناموفق'})

        return {'user': user}


class ResendEmailConfirmationSerializer(serializers.Serializer):
    email = serializers.EmailField(label='ایمیل')

    def validate(self, data):
        email = data.get('email')
        user = USER_MODEL.objects.filter(email=email, is_active=False).first()

        if not user:
            raise serializers.ValidationError({'detail': 'اطلاعات وارد شده معتبر نیست.'})

        send_confirmation_email(user)

        return data