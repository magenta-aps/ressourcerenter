from django.views.generic import TemplateView


class FrontpageView(TemplateView):
    # TODO can be replaced, just needed a landing page.
    template_name = 'administration/frontpage.html'
