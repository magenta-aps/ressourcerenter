from django.http import HttpResponse
from django.utils.formats import date_format
from django.views.generic import FormView
from openpyxl import Workbook
from datetime import date


class HistoryMixin():

    template_name_suffix = '_history'

    def get_context_data(self, **kwargs):
        qs = self.object.history.all().order_by('-history_date')
        return super().get_context_data(**{
            **kwargs,
            'model': self.model,
            'object_list': qs,
            'fields': [
                (field, self.model._meta.get_field(field))
                for field in self.get_fields()
            ],
        })

    def get_fields(self):
        return ()


class GetFormView(FormView):
    '''
    A FormView that uses the GET method
    '''
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.has_changed():
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return self.render_to_response(self.get_context_data())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['data'] = self.request.GET if len(self.request.GET) else None
        return kwargs


class ExcelMixin(object):
    excel_fields = []
    filename_base = 'spreadsheet'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        params = self.request.GET.copy()
        params['format'] = 'xlsx'
        ctx.update({
            'excel_link': '?' + params.urlencode()
        })
        return ctx

    def render_excel_file(self, context):
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()
        form = context.get('form')
        ws.append(self.headers(form))

        for row in self.rows(form):
            for i, value in enumerate(row):
                if isinstance(value, date):
                    row[i] = date_format(value, format='SHORT_DATE_FORMAT', use_l10n=True)
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={self.filename_base}.xlsx'
        wb.save(response)
        return response

    def headers(self, form):
        for header_name, data_path in self.excel_fields:
            yield header_name

    def rows(self, form):
        queryset = self.get_queryset().all()
        for item in queryset:
            row = []
            for header_name, data_path in self.excel_fields:
                value = item
                for path_part in data_path.split('__'):
                    value = getattr(value, path_part)
                    if callable(value):
                        value = value()
                row.append(value)
            yield row

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'xlsx':
            return self.render_excel_file(context)
        return super().render_to_response(context, **response_kwargs)
