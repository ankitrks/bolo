# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponsePermanentRedirect

from django.conf import  settings
from djconfig import config
from django.conf import settings

from ..core.utils.paginator import yt_paginate
from ..topic.models import Topic
from .models import Category


def detail(request, pk, slug):

    categories = Category.objects \
        .visible() \
        .parents()

    category = get_object_or_404(Category.objects.visible(),
                                 pk=pk)

    if category.slug != slug:
        return HttpResponsePermanentRedirect(category.get_absolute_url())

    subcategories = Category.objects\
        .visible()\
        .children(parent=category)

    sub_category = []
    topics = []

    if len(subcategories) > 0:
        sub_category = get_object_or_404(Category.objects.visible(), pk=subcategories[0].pk)
        topics = sub_category.category_topics.all()[0:8]

    current_index = 0

    for index, category_each in enumerate(categories):
        if category_each.id == category.id:
            current_index = index



    context = {
        'categories': categories,
        'category': category,
        'subcategories': subcategories,
        'sub_category': sub_category,
        'topics': topics,
        'current_index': current_index
    }

    return render(request, 'spirit/category/sub_category_detail.html', context)

    return render(request, 'spirit/category/detail.html', context)


def sub_detail(request, pk, slug, sub_cat_pk, sub_cat_slug):

    categories = Category.objects \
        .visible() \
        .parents()

    category = get_object_or_404(Category.objects.visible(),
                                 pk=pk)

    sub_category = get_object_or_404(Category.objects.visible(), pk=sub_cat_pk)

    if category.slug != slug:
        return HttpResponsePermanentRedirect(category.get_absolute_url())

    subcategories = Category.objects\
        .visible()\
        .children(parent=category)

    topics = sub_category.category_topics.all()[0:8]

    current_index = 0

    for index, category_each in enumerate(categories):
        if category_each.id == category.id:
            current_index = index

    context = {
        'categories': categories,
        'category': category,
        'subcategories': subcategories,
        'sub_category': sub_category,
        'topics': topics,
        'current_index': current_index
    }

    return render(request, 'spirit/category/sub_category_detail.html', context)


class IndexView(ListView):

    template_name = 'spirit/category/index.html'
    context_object_name = "categories"
    queryset = Category.objects.visible().parents()
