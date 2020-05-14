from django import template

register = template.Library()


@register.filter
def intequaltest(value, arg):
    return value == arg
