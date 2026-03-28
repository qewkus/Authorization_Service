from django.core.exceptions import ValidationError
from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):
    help = "Создание суперпользователя с email и паролем"

    def add_arguments(self, parser):
        parser.add_argument(
            "--phone", type=str, required=True, help="Номер телефона суперпользователя"
        )
        parser.add_argument(
            "--password", type=str, required=True, help="Пароль для суперпользователя"
        )

    def handle(self, *args, **options):
        phone_number = options["phone"]
        password = options["password"]

        # Проверка номера телефона
        if (
            not phone_number.startswith("+")
            or not phone_number[1:].isdigit()
            or len(phone_number) < 10
        ):
            self.stdout.write(self.style.ERROR("Некорректный формат номера телефона."))
            return

        # Проверка длины пароля
        if len(password) < 8:
            self.stdout.write(self.style.ERROR("Пароль слишком короткий."))
            return

        try:
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f"Пользователь с номером {phone_number} уже существует."
                    )
                )
                return

            user = CustomUser(phone_number=phone_number)
            user.set_password(password)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Суперпользователь с email:{phone_number} успешно создан!"
                )
            )
        except ValidationError as e:
            self.stderr.write(
                self.style.ERROR(f"Ошибка при создании пользователя: {e}.")
            )
