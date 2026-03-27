from django.urls import path

from users.apps import UsersConfig
from users.views import (
    ActivateReferralCodeView,
    LogoutProfileView,
    ProfileView,
    RequestCodeView,
    VerifyCodeView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("auth/logout/", LogoutProfileView.as_view(), name="logout"),
    path("auth/request-code/", RequestCodeView.as_view(), name="request-code"),
    path("auth/verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "referral/activate/",
        ActivateReferralCodeView.as_view(),
        name="activate-referral",
    ),
]
