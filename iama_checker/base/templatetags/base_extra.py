from django import template
from ..models import Answer

register = template.Library()

@register.filter
def key(dict, key):
    return dict[str(key)]

@register.filter
def cluster(cluster, mode):
    if mode == 0:
        return cluster["subcluster_name"]
    elif mode == 1:
        return cluster["examples"]

@register.filter
def is_reviewed(status):
    return status == Answer.Status.RV


