from rest_framework.test import APITestCase
from django.urls import reverse
from unittest.mock import patch
from rest_framework import status
from users.services import SMSService, AuthService
from users.models import CustomUser


class RequestCodeViewTest(APITestCase):
    def test_request_code(self):
        url = reverse('users:request-code')
        data = {'phone_number': '+79991234567'}

        with patch('users.services.SMSService.generate_code', return_value='1332'):
            response = self.client.post(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_302_FOUND)
            self.assertRedirects(response, reverse('users:verify-code'))


class VerifyCodeViewTest(APITestCase):
    def setUp(self):
        self.phone_number = '+79991234567'
        self.code = '1332'
        SMSService.save_code(self.phone_number, self.code)

    def test_verify_invalid_code(self):
        url = reverse('users:verify-code')
        data = {'phone_number': self.phone_number, 'code': '0000'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone_number='+79991234567')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:profile')

    def test_profile_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #print(response.data)
        self.assertEqual(response.data['user']['phone_number'], self.user.phone_number)


class ActivateReferralCodeViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone_number='+79991234567', invite_code='BRPDI5')
        self.referral = CustomUser.objects.create(phone_number='+79997654321', invite_code='CSK123')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:activate-referral')

    def test_activate_referral_code(self):
        data = {'referral_code': 'CSK123'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.user.refresh_from_db()
        self.assertEqual(self.user.referral_code, 'CSK123')

    def test_activate_referral_code_invalid(self):
        data = {'referral_code': 'invalid'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('referral_code', response.data)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.referral_code)


class LogoutProfileViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone_number='+79991234567')
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:logout')

    def test_logout(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse("users:verify-code"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_logout_requires_authentication(self):
        """Тест выхода для неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
