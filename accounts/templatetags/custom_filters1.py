from django import template

register = template.Library()

@register.filter(name='add_class_if_error')
def add_class_if_error(field, css_class):
    """
    폼 필드에 에러가 있을 경우 추가 CSS 클래스를 붙여주는 필터
    """
    existing_classes = field.field.widget.attrs.get('class', '')
    if field.errors:
        return field.as_widget(attrs={
            'class': f'{existing_classes} {css_class}'
        })
    return field.as_widget(attrs={
        'class': existing_classes
    })


@register.filter(name='add_style_if_error')
def add_style_if_error(field, style_string):
    """
    폼 필드에 에러가 있을 경우 style 속성을 추가해주는 필터
    """
    existing_style = field.field.widget.attrs.get('style', '')
    if field.errors:
        return field.as_widget(attrs={
            'style': f'{existing_style} {style_string}'
        })
    return field.as_widget(attrs={
        'style': existing_style
    })
