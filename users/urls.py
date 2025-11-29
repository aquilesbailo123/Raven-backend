from django.urls import path, include
# from django.views.generic.base import View

from .views import (
    CustomVerifyEmailView,
    ResendEmailConfirmationView,
    PasswordResetConfirmView,
    StartupOnboardingView,
    OnboardingCompleteView,
    StartupDataView,
    EvidenceListView,
    FinancialDataListView,
    InvestorPipelineListView
)

# NOTE if you replace reset-password/ with a custom view, this can be used as placeholder because dj_rest_auth needs this exact url to exist
# class NullView(View):
#     pass

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/registration/account-confirm-email/', CustomVerifyEmailView.as_view(), name='account_confirm_email'),
    path('resend-email-confirmation/', ResendEmailConfirmationView.as_view(), name='resend_email_confirmation'),
    path('reset-password/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('onboarding/startup/', StartupOnboardingView.as_view(), name='startup_onboarding'),
    path('startup/complete-onboarding/', OnboardingCompleteView.as_view(), name='complete_onboarding'),

    # Startup data endpoints
    path('startup/data/', StartupDataView.as_view(), name='startup_data'),
    path('startup/evidences/', EvidenceListView.as_view(), name='evidence_list'),
    path('startup/financial-data/', FinancialDataListView.as_view(), name='financial_data_list'),
    path('startup/investors/', InvestorPipelineListView.as_view(), name='investor_pipeline_list'),
]