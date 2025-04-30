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

@register.filter(name='subtract')
def subtract(value, arg):
    """
    Subtracts the arg from the value.
    
    Example:
    {{ 5|subtract:2 }} will output 3
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
