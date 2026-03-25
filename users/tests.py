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
            self.assertEqual(self.client.session['phone_number'], data['phone_number'])


class VerifyCodeViewTest(APITestCase):
    def setUp(self):
        self.phone_number = '+79991234567'
        self.code = '1332'
        session = self.client.session
        session['phone_number'] = self.phone_number
        session.save()
        SMSService.save_code(self.phone_number, self.code)

    def test_verify_code_get(self):
        url = reverse('users:verify-code')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.phone_number)

    def test_verify_valid_code(self):
        url = reverse('users:verify-code')
        data = {'code': self.code}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('users:profile'))
        self.assertNotIn('phone_number', self.client.session)

    def test_verify_invalid_code(self):
        url = reverse('users:verify-code')
        data = {'code': '0000'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_out_phone_number_in_session(self):
        session = self.client.session
        del session['phone_number']
        session.save()

        url = reverse('users:verify-code')
        data = {'code': self.code}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(phone_number='+79991234567', invite_code='ABC123')
        self.referred_user = CustomUser.objects.create(
            phone_number='+79997654321',
            referral_code='ABC123'  # Использует invite_code первого пользователя
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('users:profile')

    def test_profile_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что пользователь передан в контекст
        self.assertEqual(response.data['user'], self.user)
        # Проверяем список рефералов
        self.assertIn(self.referred_user, response.data['referred_users'])


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
        self.assertIn('errors', response.data)
        self.assertIn('referral_code', response.data['errors'])
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
        self.assertEqual(response.url, reverse("users:request-code"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_logout_requires_authentication(self):
        """Тест выхода для неаутентифицированного пользователя"""
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
