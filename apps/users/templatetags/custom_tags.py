from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if type(dictionary) is dict:
        return dictionary.get(key)
    return None
