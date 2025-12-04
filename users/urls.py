from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from django.views.generic.base import View

from .views import (
    CustomVerifyEmailView,
    ResendEmailConfirmationView,
    PasswordResetConfirmView,
    StartupOnboardingView,
    OnboardingCompleteView,
    StartupDataView,
    # EvidenceListView, # Removed
    FinancialDataListView,
    InvestorPipelineListView,
    # RoundViewSet, # Replaced by campaigns.views.RoundViewSet
    EvidenceViewSet, # Added EvidenceViewSet
    ReadinessLevelViewSet,
)
from campaigns.views import RoundViewSet

# NOTE if you replace reset-password/ with a custom view, this can be used as placeholder because dj_rest_auth needs this exact url to exist
# class NullView(View):
#     pass

router = DefaultRouter()
router.register(r'startup/rounds', RoundViewSet, basename='startup-round') # Registered RoundViewSet
router.register(r'startup/evidences', EvidenceViewSet, basename='startup-evidence') # Registered EvidenceViewSet
router.register(r'startup/readiness-levels', ReadinessLevelViewSet, basename='startup-readiness-level')

from .views_incubator import (
    IncubatorViewSet,
    IncubatorMemberViewSet,
    ChallengeViewSet,
    ChallengeApplicationViewSet,
    StartupIncubatorAssociationViewSet,
    IncubatorOnboardingView,
    IncubatorDataView,
    IncubatorInvestmentViewSet,
    PortfolioEvidenceViewSet,
    PortfolioReadinessLevelViewSet,
    PortfolioCampaignViewSet
)

router.register(r'incubators', IncubatorViewSet)
router.register(r'incubator/members', IncubatorMemberViewSet, basename='incubator-member')
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'challenge-applications', ChallengeApplicationViewSet, basename='challenge-application')
router.register(r'startup/associate-incubator', StartupIncubatorAssociationViewSet, basename='startup-incubator-associate')
router.register(r'incubator/investments', IncubatorInvestmentViewSet, basename='incubator-investment')
router.register(r'incubator/portfolio/evidences', PortfolioEvidenceViewSet, basename='portfolio-evidence')
router.register(r'incubator/portfolio/readiness-levels', PortfolioReadinessLevelViewSet, basename='portfolio-readiness-level')
router.register(r'incubator/portfolio/campaigns', PortfolioCampaignViewSet, basename='portfolio-campaign')

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/registration/account-confirm-email/', CustomVerifyEmailView.as_view(), name='account_confirm_email'),
    path('resend-email-confirmation/', ResendEmailConfirmationView.as_view(), name='resend_email_confirmation'),
    path('reset-password/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('onboarding/startup/', StartupOnboardingView.as_view(), name='startup_onboarding'),
    path('incubator/complete-onboarding/', IncubatorOnboardingView.as_view(), name='incubator_complete_onboarding'),
    path('incubator/data/', IncubatorDataView.as_view(), name='incubator_data'),
    path('startup/complete-onboarding/', OnboardingCompleteView.as_view(), name='complete_onboarding'),

    # Startup data endpoints
    path('startup/data/', StartupDataView.as_view(), name='startup_data'),
    # path('startup/evidences/', EvidenceListView.as_view(), name='evidence_list'), # Removed
    path('startup/financial-data/', FinancialDataListView.as_view(), name='financial_data_list'),
    path('startup/investors/', InvestorPipelineListView.as_view(), name='investor_pipeline_list'),

    # Include router URLs for startup rounds and evidences
    path('', include(router.urls)),
    path('', include(router.urls)),
]