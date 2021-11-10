from django.views.generic import TemplateView


class CreateInberetningCreateView(TemplateView):
    template_name = 'indberetning/create.html'


class CompanySelect(TemplateView):
    template_name = 'indberetning/company_select.html'


class IndberetningsListView(TemplateView):
    template_name = 'indberetning/list.html'
