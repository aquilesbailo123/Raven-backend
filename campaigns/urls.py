from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, RoundViewSet

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'rounds', RoundViewSet, basename='round')

urlpatterns = [
    path('', include(router.urls)),
]
