## Code extracted (and adapted) from django-model-utils/managers.py
## See: https://github.com/carljm/django-model-utils
##
##    Copyright (c) 2009-2013, Carl Meyer and contributors
##    All rights reserved.
##    
##    Redistribution and use in source and binary forms, with or without
##    modification, are permitted provided that the following conditions are
##    met:
##    
##        * Redistributions of source code must retain the above copyright
##          notice, this list of conditions and the following disclaimer.
##        * Redistributions in binary form must reproduce the above
##          copyright notice, this list of conditions and the following
##          disclaimer in the documentation and/or other materials provided
##          with the distribution.
##        * Neither the name of the author nor the names of other
##          contributors may be used to endorse or promote products derived
##          from this software without specific prior written permission.
##    
##    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
##    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
##    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
##    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
##    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
##    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
##    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
##    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
##    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
##    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals
import django
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist

try:
    from django.db.models.constants import LOOKUP_SEP
except ImportError: # Django < 1.5
    from django.db.models.sql.constants import LOOKUP_SEP

class InheritanceQuerySet(QuerySet):
    def select_subclasses(self, *subclasses):
        if not subclasses:
            # only recurse one level on Django < 1.6 to avoid triggering
            # https://code.djangoproject.com/ticket/16572
            levels = None
            if django.VERSION < (1, 6, 0):
                levels = 1
            subclasses = self._get_subclasses_recurse(self.model, levels=levels)
        # workaround https://code.djangoproject.com/ticket/16855
        field_dict = self.query.select_related
        new_qs = self.select_related(*subclasses)
        if isinstance(new_qs.query.select_related, dict) and isinstance(field_dict, dict):
            new_qs.query.select_related.update(field_dict)
        new_qs.subclasses = subclasses
        return new_qs


    def _clone(self, klass=None, setup=False, **kwargs):
        for name in ['subclasses', '_annotated']:
            if hasattr(self, name):
                kwargs[name] = getattr(self, name)
        return super(InheritanceQuerySet, self)._clone(klass, setup, **kwargs)


    def annotate(self, *args, **kwargs):
        qset = super(InheritanceQuerySet, self).annotate(*args, **kwargs)
        qset._annotated = [a.default_alias for a in args] + list(kwargs.keys())
        return qset


    def iterator(self):
        iter = super(InheritanceQuerySet, self).iterator()
        if getattr(self, 'subclasses', False):
            # sort the subclass names longest first,
            # so with 'a' and 'a__b' it goes as deep as possible
            subclasses = sorted(self.subclasses, key=len, reverse=True)
            for obj in iter:
                sub_obj = None
                for s in subclasses:
                    sub_obj = self._get_sub_obj_recurse(obj, s)
                    if sub_obj:
                        break
                if not sub_obj:
                    sub_obj = obj

                if getattr(self, '_annotated', False):
                    for k in self._annotated:
                        setattr(sub_obj, k, getattr(obj, k))

                yield sub_obj
        else:
            for obj in iter:
                yield obj


    def _get_subclasses_recurse(self, model, levels=None):
        rels = [rel for rel in model._meta.get_all_related_objects()
                      if isinstance(rel.field, OneToOneField)
                      and issubclass(rel.field.model, model)]
        subclasses = []
        if levels:
            levels -= 1
        for rel in rels:
            if levels or levels is None:
                for subclass in self._get_subclasses_recurse(
                        rel.field.model, levels=levels):
                    subclasses.append(rel.var_name + LOOKUP_SEP + subclass)
            subclasses.append(rel.var_name)
        return subclasses


    def _get_sub_obj_recurse(self, obj, s):
        rel, _, s = s.partition(LOOKUP_SEP)
        try:
            node = getattr(obj, rel)
        except ObjectDoesNotExist:
            return None
        if s:
            child = self._get_sub_obj_recurse(node, s)
            return child
        else:
            return node



class InheritanceManager(models.Manager):
    """
    Introduces select_subclasses and get_subclass methods that return
    instances of child class models rather than the super class.
    """
    use_for_related_fields = True

    def get_queryset(self):
        """get_queryset in django 1.6 / get_query_set before that."""
##        return InheritanceQuerySet(self.model)  ## original configuration
        return InheritanceQuerySet(self.model)

    def select_subclasses(self, *subclasses):
        return self.get_query_set().select_subclasses(*subclasses)

    def get_subclass(self, *args, **kwargs):
        return self.get_query_set().select_subclasses().get(*args, **kwargs)
