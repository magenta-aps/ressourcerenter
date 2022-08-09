class HistoryMixin:

    template_name_suffix = "_history"

    def get_context_data(self, **kwargs):
        qs = self.object.history.all().order_by("-history_date")
        return super().get_context_data(
            **{
                **kwargs,
                "model": self.model,
                "object_list": qs,
                "fields": [
                    (field, self.model._meta.get_field(field))
                    for field in self.get_fields()
                ],
            }
        )

    def get_fields(self):
        return ()
