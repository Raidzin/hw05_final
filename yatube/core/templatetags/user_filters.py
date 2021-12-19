from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def uglify(text):
    new_text = ''
    for i in range(len(text)):
        if i % 2 == 0:
            new_text += text[i].upper()
        else:
            new_text += text[i].lower()
    return new_text
