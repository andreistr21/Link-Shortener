from django import template

register = template.Library()


@register.filter()
def remove_attr(field, attr):
    if attr in field.field.widget.attrs:
        del field.field.widget.attrs[attr]
    return field