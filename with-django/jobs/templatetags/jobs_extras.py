from django import template

register = template.Library()

@register.filter(name='index')
def index(value, arg):
    """
    Returns the item at the specified index from a list or a dictionary value by key.
    
    Example:
    {{ mylist|index:0 }}
    {{ mydict|index:'key' }}
    """
    try:
        if isinstance(value, dict):
            return value.get(arg, '')
        return value[arg]
    except (IndexError, KeyError, TypeError):
        return ''
