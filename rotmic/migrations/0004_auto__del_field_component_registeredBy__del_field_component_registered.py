# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Component.registeredBy'
        db.delete_column(u'rotmic_component', 'registeredBy_id')

        # Deleting field 'Component.registeredAt'
        db.delete_column(u'rotmic_component', 'registeredAt')


    def backwards(self, orm):
        # Adding field 'Component.registeredBy'
        db.add_column(u'rotmic_component', 'registeredBy',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='component_created_by', null=True, to=orm['auth.User'], blank=True),
                      keep_default=False)

        # Adding field 'Component.registeredAt'
        db.add_column(u'rotmic_component', 'registeredAt',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 8, 11, 0, 0)),
                      keep_default=False)


    models = {
        'rotmic.component': {
            'Meta': {'object_name': 'Component'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'planning'", 'max_length': '30'})
        },
        'rotmic.dnacomponent': {
            'Meta': {'object_name': 'DnaComponent', '_ormbases': ['rotmic.Component']},
            'circular': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'insert': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Insert'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'marker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'marker_rel_+'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vectorBackbone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.DnaComponent']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rotmic']