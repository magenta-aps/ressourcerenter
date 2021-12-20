from django.http import HttpResponse
from django.utils.formats import date_format
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


class ExcelMixin(object):
    excel_fields = []
    filename = 'spreadsheet.xlsx'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        params = self.request.GET.copy()
        params['format'] = 'excel'
        ctx.update({
            'excel_link': '?' + params.urlencode()
        })
        return ctx

    def render_excel_file(self, queryset):
        wb = Workbook(write_only=True)
        ws = wb.create_sheet()
        ws.append([header_name for header_name, data_path in self.excel_fields])

        for item in queryset.all():
            row = []
            for header_name, data_path in self.excel_fields:
                value = item
                for path_part in data_path.split('__'):
                    value = getattr(value, path_part)
                    if callable(value):
                        value = value()
                row.append(value)

            for i, value in enumerate(row):
                if isinstance(value, date):
                    row[i] = date_format(value, format='SHORT_DATE_FORMAT', use_l10n=True)
            ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={}'.format(self.filename)
        wb.save(response)
        return response

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('format') == 'excel':
            return self.render_excel_file(self.get_queryset())
        return super().render_to_response(context, **response_kwargs)
