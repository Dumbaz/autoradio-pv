from django import template

from program.models import Type, MusicFocus, Category, Topic

register = template.Library()


@register.inclusion_tag('boxes/type.html')
def type():
    return {'type_list': Type.objects.filter(enabled=True)}


@register.inclusion_tag('boxes/musicfocus.html')
def musicfocus():
    return {'musicfocus_list': MusicFocus.objects.all()}


@register.inclusion_tag('boxes/category.html')
def category():
    return {'category_list': Category.objects.all()}


@register.inclusion_tag('boxes/topic.html')
def topic():
    return {'topic_list': Topic.objects.all()}