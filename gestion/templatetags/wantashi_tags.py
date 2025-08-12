from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(value, arg):
    """
    Adds a CSS class to a form field widget
    Usage: {{ field|addclass:"custom-class" }}
    """
    return value.as_widget(attrs={'class': f'{value.field.widget.attrs.get("class", "")} {arg}'.strip()})
