from django import template
from ..models import Answer

register = template.Library()

@register.filter()
def key(dict, key):
    return dict[str(key)]

@register.filter()
def is_reviewed(status):
    return status == Answer.Status.RV