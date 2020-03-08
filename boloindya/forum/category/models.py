# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils import timezone

from ..core.conf import settings
from ..core.utils.models import AutoSlugField
from .managers import CategoryQuerySet
from drf_spirit.utils import language_options


class Category(models.Model):
    """
    Category model

    :ivar reindex_at: Last time this model was marked\
    for reindex. It makes the search re-index the topic,\
    it must be set explicitly
    :vartype reindex_at: `:py:class:models.DateTimeField`
    """
    parent = models.ForeignKey('self', verbose_name=_("category parent"), null=True, blank=True , related_name="parent_category")

    title = models.CharField(_("title"), max_length=75)
    hindi_title = models.CharField(_("hindi_title"), max_length=75,null=True,blank=True)
    tamil_title = models.CharField(_("tamil_title"), max_length=75,null=True,blank=True)
    telgu_title = models.CharField(_("telgu_title"), max_length=75,null=True,blank=True)
    bengali_title = models.CharField(_("bengali_title"), max_length=75,null=True,blank=True)
    kannada_title = models.CharField(_("kannada_title"), max_length=75,null=True,blank=True)
    malayalam_title = models.CharField(_("malayalam_title"), max_length=75,null=True,blank=True)
    gujrati_title = models.CharField(_("gujrati_title"), max_length=75,null=True,blank=True)
    marathi_title = models.CharField(_("marathi_title"), max_length=75,null=True,blank=True)
    punjabi_title = models.CharField(_("punjabi_title"), max_length=75,null=True,blank=True)
    odia_title = models.CharField(_("odia_title"), max_length=75,null=True,blank=True)
    slug = AutoSlugField(populate_from="title", db_index=False, blank=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    color = models.CharField(_("color"), max_length=7, blank=True,
                             help_text=_("Title color in hex format (i.e: #1aafd0)."))
    reindex_at = models.DateTimeField(_("modified at"), default=timezone.now)

    is_global = models.BooleanField(_("global"), default=True,
                                    help_text=_('Designates whether the topics will be'
                                                'displayed in the all-categories list.'))
    is_closed = models.BooleanField(_("closed"), default=False)
    is_removed = models.BooleanField(_("removed"), default=False)
    is_private = models.BooleanField(_("private"), default=False)
    category_image = models.CharField(_("Category Image URL"), max_length=150, blank=True)
    dark_category_image = models.CharField(_("Dark Category Image URL"), max_length=150, blank=True)
    order_no = models.IntegerField(default = 0)
    view_count = models.BigIntegerField(default = 0)
    is_engagement = models.BooleanField(default=False)

    objects = CategoryQuerySet.as_manager()

    def __unicode__(self):
        return self.title
        # if not self.parent:
        #     return self.title
        # return self.title + ' [' + self.parent.title + ']'

    class Meta:
        ordering = ['order_no']
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def get_absolute_url(self):
        if self.pk == settings.ST_TOPIC_PRIVATE_CATEGORY_PK:
            return reverse('spirit:topic:private:index')
        else:
            return reverse(
                'spirit:category:detail',
                kwargs={'pk': str(self.id), 'slug': self.slug})

    @property
    def is_subcategory(self):
        if self.parent_id:
            return True
        else:
            return False

class CategoryViewCounter(models.Model):
    category = models.ForeignKey('forum_category.Category', verbose_name=_("category"), related_name="category_counter",null=True,blank=True)
    language = models.CharField(_("language"), choices=language_options, blank = True, null = True, max_length=10)
    view_count = models.BigIntegerField(default = 0)

    class Meta:
        ordering = ['language']
    
    def __unicode__(self):
        return str(self.category)+"---"+str(self.get_language_display())