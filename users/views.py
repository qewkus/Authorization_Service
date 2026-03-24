from django.contrib.auth import login, logout
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from django.shortcuts import redirect
from .serializers import (
    PhoneNumberSerializer,
    VerifyCodeSerializer,
    ProfileCustomUserSerializer,
    ReferralCodeSerializer,
)
from .services import SMSService, AuthService, ReferralService


class RequestCodeView(APIView):
    """Представление для запроса кода подтверждения"""
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/request_code.html'

    def get(self, request):
        serializer = PhoneNumberSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})

        phone_number = serializer.validated_data['phone_number']
        code = SMSService.generate_code()

        SMSService.save_code(phone_number, code)  # Сохраняю код в Редис

        SMSService.send_sms(phone_number, code)  # Отправляю смс с кодом

        return redirect('users:verify-code')


class VerifyCodeView(APIView):
    """Представление для проверки кода подтверждения"""
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/verify_code.html'

    def get(self, request):
        serializer = VerifyCodeSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})

        phone_number = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']

        try:
            user, tokens = AuthService.authenticate(phone_number, code)
            if user is not None:
                login(request, user)
            response = redirect('users:profile')
            response.set_cookie('access', tokens['access'])
            response.set_cookie('refresh', tokens['refresh'])
            return response
        except ValueError as e:
            return Response({
                'serializer': serializer,
                'error': str(e)
            })


class ProfileView(generics.RetrieveUpdateAPIView):
    """Представление для просмотра и обновления профиля"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/profile.html'
    serializer_class = ProfileCustomUserSerializer

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return Response({
            'user': self.object,
            'serializer': self.get_serializer(self.object)
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(self.object, data=request.data)
        if not serializer.is_valid():
            return Response({
                'user': self.object,
                'serializer': serializer
            })
        serializer.save()
        return redirect('users:profile')

    def get_object(self):
        return self.request.user


class ActivateReferralCodeView(APIView):
    """Представление для активации реферального кода"""
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'users/activate_referral.html'

    def get(self, request):
        serializer = ReferralCodeSerializer()
        return Response({'serializer': serializer})

    def post(self, request):
        serializer = ReferralCodeSerializer(
            data=request.data,
            context={'user': request.user}
        )
        if not serializer.is_valid():
            return Response({'serializer': serializer})

        try:
            ReferralService.activate_referral_code(
                request.user,
                serializer.validated_data['referral_code']
            )
            return redirect('users:profile')
        except Exception as e:
            return Response({
                'serializer': serializer,
                'error': str(e)
            })


class LogoutProfileView(APIView):
    """Представление для выхода из профиля"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        response = redirect("users:verify-code")
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response
