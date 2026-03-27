from django.core.validators import RegexValidator
from rest_framework import serializers

from .models import CustomUser

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр разрешено.",
)

code_regex = RegexValidator(
    regex="^[0-9]*$", message="Код должен содержать только цифры"
)

invite_code_regex = RegexValidator(
    regex="^[A-Z0-9]*$",
    message="Инвайт-код должен содержать только заглавные буквы и цифры",
)


def validate_phone_number(value: str) -> str:
    """Валидация и форматирование номера телефона"""

    cleaned_number = "".join(filter(str.isdigit, value))

    if len(cleaned_number) == 10:
        cleaned_number = "+7" + cleaned_number
    elif len(cleaned_number) == 11:
        if cleaned_number[0] in ["7", "8"]:
            cleaned_number = "+7" + cleaned_number[1:]
        else:
            raise serializers.ValidationError("Неверный формат номера телефона")
    elif len(cleaned_number) == 12 and cleaned_number.startswith("7"):
        cleaned_number = "+" + cleaned_number
    else:
        raise serializers.ValidationError("Неверный формат номера телефона")

    return cleaned_number


def validate_verification_code(value: str) -> str:
    """Валидация кода подтверждения"""
    if not value.isdigit() or len(value) != 4:
        raise serializers.ValidationError("Код должен состоять из 4 цифр")
    return value


def validate_referral_code(value: str, user=None) -> str:
    """Валидация реферального кода"""
    if not value:
        return value

    if user and user.referral_code:
        raise serializers.ValidationError("Вы уже активировали инвайт-код")

    if not CustomUser.objects.filter(invite_code=value).exists():
        raise serializers.ValidationError("Указанный инвайт-код не существует")

    if user and value == user.invite_code:
        raise serializers.ValidationError("Нельзя использовать собственный инвайт-код")

    return value
