from rest_framework import serializers as s

from users.models import CustomUser


class CustomUserSerializer(s.ModelSerializer):
    """Главный сериализатор для модели CustomUser. Необходим для создания и обновления пользователей"""
    class Meta:
        model = CustomUser
        fields = ["id", "phone_number", "invite_code", "referral_code",]
        read_only_fields = ["invite_code",]


class ProfileCustomUserSerializer(s.ModelSerializer):
    """Сериализатор для профиля пользователя со списком номеров телефонов рефералов."""
    referred_users = s.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "phone_number", "invite_code", "referral_code", "referred_users",]
        read_only_fields = ["invite_code", "referred_users",]

    def get_referred_users(self, obj):
        """Получаем список номеров рефералов используя метод модели get_referred_users"""
        return obj.get_referred_users()
    