
from django.views.generic import RedirectView, TemplateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView

class AdStatsDashboardView(TemplateView):
    template_name = 'advertisement/stats/index.html'


class LoginView(LoginView):
    template_name = 'marketing/registration/login.html'
    success_url = '/marketing/ad/install/stats/'

    def get_success_url(self):
        return self.success_url


class LogoutView(LogoutView):
    next_page = '/marketing/login/'

class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'marketing/registration/reset_password.html'
    success_url = '/marketing/login/?password_changed=success'


class PasswordResetMailView(PasswordResetView):
    template_name = 'marketing/registration/login.html'
    success_url = '/marketing/login/?reset_password=success'
    html_email_template_name = 'marketing/registration/password_reset_email.html'
    email_template_name = 'marketing/registration/password_reset_email.html'
