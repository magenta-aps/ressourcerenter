from django.template.defaultfilters import register
from django.utils.translation import gettext as _


@register.filter
def get(item, attribute):
    if hasattr(item, attribute):
        return getattr(item, attribute)
    if hasattr(item, 'get'):
        return item.get(attribute)
    if isinstance(item, (tuple, list)):
        return item[int(attribute)]


@register.filter
def janej(item):
    if type(item) == bool:
        return _('ja') if item else _('nej')
    return item


@register.filter
def list_sum_attr(itemlist, attribute):
    return sum([getattr(item, attribute) for item in itemlist])
