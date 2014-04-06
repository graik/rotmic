from django.utils.safestring import mark_safe
from django import template

import ratedcomments

register = template.Library()

@register.filter(name='restyle')
def restyle(field, css):
    """
    from: http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
    Add additional CSS or style tags to a django-rendered field directly in template.
    
    Usage: {{ form.field | restyle:"text-align:right" }}
    """
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
            
    return field.as_widget(attrs=attrs)


@register.assignment_tag
def recentcomments(n=10):
    qs = ratedcomments.get_model().objects.filter(
            is_removed = False,
        )
    return qs.order_by('-submit_date')[:n]