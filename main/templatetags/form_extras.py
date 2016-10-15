from django import template

register = template.Library()

@register.filter(name='fieldlabel')
def fieldlabel(field, cls):
    return field.label_tag(attrs={'class': cls})

@register.filter(name='fieldcss')
def fieldcss(field, cls):
    return field.as_widget(attrs={'class': cls})
