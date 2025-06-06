from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('login', login.as_view(), name='login'),
    path('get-access-token', TokenRefreshView.as_view(), name='get-access-token'),
    path('register', CustomUserCreate.as_view(), name="register-user"),
    path('logout', BlacklistTokenUpdateView.as_view(), name='blacklist' or 'logout'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('profile', ProfileView.as_view(),name = 'profile-view'),
    path('activate/<token>', ActivateAccount.as_view(), name='activate-account'),
    path('forgot-password', ForgotPassword.as_view(), name='forgot-password'),
    path('forget-password/confirm', ResetPassword.as_view(), name='reset-password'),
    path('delete-account', RequestAccountDeletion.as_view(), name='request-delete-account'),
    path('delete-account/confirm', ConfirmAccountDeletion.as_view(), name='delete-account'),
]

urlpatterns += router.urls