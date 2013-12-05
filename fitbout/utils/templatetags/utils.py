from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, path):
    request_path = context.get('request_path')

    if request_path == path:
        return active

    elif path != '/' and request_path.startswith(path):
        return 'active'

    return ''
