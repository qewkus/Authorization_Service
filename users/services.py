from smsaero import SmsAero
from config.settings import SMSAERO_API_KEY, SMSAERO_EMAIL


def send_sms(phone: int, message: str) -> dict:
    """Интеграция сервиса по отправке СМС кода."""
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)