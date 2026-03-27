import random
import string
from typing import List

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Номер телефона",
        help_text="Укажите номер телефона",
    )
    invite_code = models.CharField(max_length=6, unique=True, verbose_name="Инвайт-код")
    referral_code = models.CharField(
        max_length=6, null=True, blank=True, verbose_name="Пригласительный инвайт-код"
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.phone_number

    def save(self, *args, **kwargs):
        if not self.invite_code:
            while True:
                invite_code = self.generate_invite_code()
                if not CustomUser.objects.filter(invite_code=invite_code).exists():
                    self.invite_code = invite_code
                    break
        super().save(*args, **kwargs)

    @staticmethod
    def generate_invite_code():
        """Функция генерации инвайт кода"""
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def get_referred_users(self) -> List[str]:
        """Функция возвращающая список номеров телефонов, которые использовали инвайт-код данного пользователя."""
        return list(
            CustomUser.objects.filter(referral_code=self.invite_code).values_list(
                "phone_number", flat=True
            )
        )
