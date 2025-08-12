from django import template

register = template.Library()


@register.filter
def range(value):
    """Permet de créer une plage de nombres de 0 à value."""
    try:
        return range(int(value))
    except ValueError:
        return []
