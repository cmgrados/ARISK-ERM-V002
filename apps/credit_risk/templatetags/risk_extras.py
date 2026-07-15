from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key) or dictionary.get(str(key))

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def format_num(value, decimals=2):
    try:
        # Forzamos formato US: coma para miles, punto para decimales
        return "{:,.{}f}".format(float(value or 0), decimals)
    except (ValueError, TypeError):
        return value

@register.filter
def format_int(value):
    try:
        # Forzamos formato US: coma para miles
        return "{:,}".format(int(float(value or 0)))
    except (ValueError, TypeError):
        return value

@register.filter
def sub(value, arg):
    try:
        return float(value or 0) - float(arg or 0)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value or 0) * float(arg or 0)
    except (ValueError, TypeError):
        return 0
