import os
from datetime import date
from tempfile import NamedTemporaryFile

from django.db.models import Func
from django.http import HttpResponse
from django.utils.formats import date_format
from django.views.generic import FormView
from openpyxl import Workbook
from openpyxl.cell import Cell


class Trunc(Func):
    function = "TRUNC"


class GetFormView(FormView):
    """
    A FormView that uses the GET method
    """

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.has_changed():
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["data"] = self.request.GET if len(self.request.GET) else None
        return kwargs


class ExcelMixin(object):
    excel_fields = []
    filename_base = "spreadsheet"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        params = self.request.GET.copy()
        params["format"] = "xlsx"
        ctx.update({"excel_link": "?" + params.urlencode()})
        return ctx

    def create_workbook(self, context):
        wb = Workbook()
        try:
            ws = wb.worksheets[0]
        except IndexError:
            ws = wb.create_sheet()
        form = context.get("form")
        ws.append(self.headers(form))

        for row in self.rows(form):
            for i, item in enumerate(row):
                value = item["value"] if type(item) is dict else item

                if isinstance(value, date):
                    value = date_format(
                        value, format="SHORT_DATE_FORMAT", use_l10n=True
                    )

                if type(item) is dict and "excel_format" in item:
                    value = Cell(worksheet=ws, value=value)
                    value.number_format = item["excel_format"]

                row[i] = value
            ws.append(row)
        return wb

    def render_excel_file(self, context):
        wb = self.create_workbook(context)

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
            response = HttpResponse(
                content=stream,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                f"attachment; filename={self.filename_base}.xlsx"
            )
            return response

    def create_excel_file(self, context, filename):
        wb = self.create_workbook(context)
        folder = os.path.dirname(filename)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        wb.save(filename)

    def headers(self, form):
        for header_name, data_path in self.excel_fields:
            yield header_name

    def rows(self, form):
        items = self.get_queryset().all()
        for item in items:
            row = []
            for header_name, data_path in self.excel_fields:
                value = item
                for path_part in data_path.split("__"):
                    value = getattr(value, path_part)
                    if callable(value):
                        value = value()
                row.append(value)
            yield row

    def render_to_response(self, context, **response_kwargs):
        if "xlsx" in (self.request.GET.get("format"), self.request.POST.get("format")):
            return self.render_excel_file(context)
        return super().render_to_response(context, **response_kwargs)
