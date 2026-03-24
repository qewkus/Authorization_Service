from smsaero import SmsAero
from config.settings import SMSAERO_API_KEY, SMSAERO_EMAIL
import random
from typing import Tuple
from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser


class SMSService:
    """Сервис для работы с SMS"""
    @staticmethod
    def generate_code() -> str:
        """Генерация 4-значного кода подтверждения"""
        return str(random.randint(1000, 9999))

    @staticmethod
    def save_code(phone_number: str, code: str) -> None:
        """Сохранение кода в Redis"""
        cache.set(f"sms_code_{phone_number}", code, timeout=300)  # Кеширую на 5 минут

    @staticmethod
    def get_code(phone_number: str) -> str:
        """Получение кода из Redis"""
        return cache.get(f"sms_code_{phone_number}")

    @staticmethod
    def delete_code(phone_number: str) -> None:
        """Удаление кода из Redis"""
        cache.delete(f"sms_code_{phone_number}")

    @staticmethod
    def send_sms(phone_number: str, code: str) -> bool:
        """Отправка SMS через SmsAero"""
        if settings.DEBUG:
            print(f"SMS code for {phone_number}: {code}")
            return True

        try:
            phone_number_int = int(phone_number)
            api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
            result = api.send_sms(phone_number_int, f"Ваш код подтверждения: {code}")
            return bool(result.get('success'))
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False


class AuthService:
    """Сервис аутентификации"""

    @staticmethod
    def get_tokens_for_user(user: CustomUser) -> dict:
        """Получение JWT токенов для пользователя"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def get_or_create_user(phone_number: str) -> Tuple[CustomUser, bool]:
        """Получение или создание пользователя по номеру телефона"""
        return CustomUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'is_active': True
            }
        )

    @classmethod
    def authenticate(cls, phone_number: str, code: str) -> Tuple[CustomUser, dict]:
        """Аутентификация пользователя по номеру телефона и коду"""
        saved_code = SMSService.get_code(phone_number)

        if not saved_code or saved_code != code:
            raise ValueError("Неверный код подтверждения")

        user, created = cls.get_or_create_user(phone_number)
        tokens = cls.get_tokens_for_user(user)

        SMSService.delete_code(phone_number)

        return user, tokens


class ReferralService:
    """Сервис для работы с реферальной системой"""

    @staticmethod
    def activate_referral_code(user: CustomUser, referral_code: str) -> None:
        """Активация реферального кода для пользователя"""
        user.referral_code = referral_code
        user.save()
