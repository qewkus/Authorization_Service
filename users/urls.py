from django.urls import path
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenRefreshView
from users.views import RequestCodeView, VerifyCodeView, ProfileView, ActivateReferralCodeView


app_name = UsersConfig.name

urlpatterns = [
    # Аутентификация
    path('auth/request-code/', RequestCodeView.as_view(), name='request-code'),
    path('auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Профиль и рефералы
    path('profile/', ProfileView.as_view(), name='profile'),
    path('referral/activate/', ActivateReferralCodeView.as_view(), name='activate-referral'),
]