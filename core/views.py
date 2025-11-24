from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class AuthenticatedLandingView(LoginRequiredMixin, TemplateView):
    """Landing page that requires user authentication"""
    template_name = 'landing.html'
    login_url = '/auth/login/'  # Redirect to API login endpoint if not authenticated
