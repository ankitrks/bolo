
from django.views.generic import RedirectView, TemplateView, DetailView

class AdStatsDashboardView(TemplateView):
    template_name = 'advertisement/stats/index.html'


