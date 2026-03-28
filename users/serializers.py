from rest_framework import serializers

from .models import CustomUser
from .validators import (
    code_regex,
    invite_code_regex,
    phone_regex,
    validate_phone_number,
    validate_referral_code,
    validate_verification_code,
)


class PhoneNumberSerializer(serializers.Serializer):
    """Сериализатор для получения номера телефона"""

    phone_number = serializers.CharField(
        validators=[phone_regex], max_length=15, help_text="Формат: +7XXXXXXXXXX"
    )

    def validate_phone_number(self, value):
        return validate_phone_number(value)


class VerifyCodeSerializer(serializers.Serializer):
    """Сериализатор для проверки кода подтверждения"""

    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4, min_length=4, validators=[code_regex])

    def validate_phone_number(self, value):
        return validate_phone_number(value)

    def validate_code(self, value):
        return validate_verification_code(value)


class ProfileCustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя со списком рефералов"""

    referred_users = serializers.SerializerMethodField()
    referral_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "phone_number",
            "invite_code",
            "referral_code",
            "referred_users",
            "referral_count",
        ]
        read_only_fields = [
            "invite_code",
            "phone_number",
            "referred_users",
            "referral_count",
        ]

    def get_referred_users(self, obj):
        return obj.get_referred_users()

    def get_referral_count(self, obj):
        return len(obj.get_referred_users())


class ReferralCodeSerializer(serializers.Serializer):
    """Сериализатор для активации реферального кода"""

    referral_code = serializers.CharField(
        max_length=6, min_length=6, validators=[invite_code_regex]
    )

    def validate_referral_code(self, value):
        return validate_referral_code(value, self.context.get("user"))
