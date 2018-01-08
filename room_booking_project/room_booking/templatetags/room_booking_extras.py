from django import template

register = template.Library()


@register.simple_tag()
def multiply(qty, price):
    return qty * price
