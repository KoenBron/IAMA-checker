from django import template
from ..models import Answer, Law

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

@register.filter
def get_law_status(status):
    match status:
        case Law.Status.CP:
            return "<i class='material-icons' style='color: green'>done</i>"
        case Law.Status.ICP:
            return "<i class='material-icons' style='color: red'>close</i>"
        case _:
            return "<i class='material-icons' style='color: yellow'>remove</i>"


