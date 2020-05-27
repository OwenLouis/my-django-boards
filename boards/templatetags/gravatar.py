# -*- coding:utf-8 -*-

from django import template
from libgravatar import Gravatar

register = template.Library()


@register.filter
def gravatar(user):
    email = user.email.lower()
    url = Gravatar(email).get_image(size=256)
    return url
