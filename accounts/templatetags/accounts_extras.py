from django import template

register = template.Library()


def social_status(value):
    status = "Male" if value == "M" else "Female"
    return status


register.filter('social_status', social_status)
