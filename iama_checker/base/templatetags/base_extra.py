from django import template

register = template.Library()

@register.filter()
def key(dict, key):
    return dict[str(key)]