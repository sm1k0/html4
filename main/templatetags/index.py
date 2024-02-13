from django import template
register = template.Library()

@register.filter
def index(indexable, i):
    return int(indexable[i])
