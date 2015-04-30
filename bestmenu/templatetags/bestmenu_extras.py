from django import template
from bestmenu.models import Category

register = template.Library()

@register.inclusion_tag('bestmenu/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all().order_by('-likes', 'name'), 'act_cat': cat}
