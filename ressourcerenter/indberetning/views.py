from django.views.generic import TemplateView


class CreateInberetningCreateView(TemplateView):
    template_name = 'indberetning/create.html'


class CreateIndhandlingsCreateView(TemplateView):
    template_name = 'indberetning/create.html'

    def get_context_data(self, **kwargs):
        ctx = super(CreateIndhandlingsCreateView, self).get_context_data(**kwargs)
        ctx.update({"indberetnings_type": "indhandling"})
        return ctx


class CompanySelect(TemplateView):
    template_name = 'indberetning/company_select.html'


class IndberetningsListView(TemplateView):
    template_name = 'indberetning/list.html'


class SelectIndberetningsType(TemplateView):
    template_name = 'indberetning/type_select.html'
