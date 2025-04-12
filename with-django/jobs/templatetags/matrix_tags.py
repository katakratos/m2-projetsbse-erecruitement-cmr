from django import template

register = template.Library()

@register.filter
def index(lst, i):
    """Returns the item at index i in the list or array"""
    try:
        return lst[i]
    except (IndexError, TypeError):
        return None
