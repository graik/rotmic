# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Component'
        db.create_table(u'rotmic_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('displayId', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='planning', max_length=30)),
        ))
        db.send_create_signal('rotmic', ['Component'])

        # Adding model 'DnaComponent'
        db.create_table(u'rotmic_dnacomponent', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['rotmic.Component'], unique=True, primary_key=True)),
            ('sequence', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('componentType', self.gf('django.db.models.fields.related.ForeignKey')(related_name='Type', to=orm['rotmic.DnaComponentType'])),
            ('insert', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='Insert', null=True, to=orm['rotmic.DnaComponent'])),
            ('vectorBackbone', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rotmic.DnaComponent'], null=True, blank=True)),
        ))
        db.send_create_signal('rotmic', ['DnaComponent'])

        # Adding M2M table for field marker on 'DnaComponent'
        m2m_table_name = db.shorten_name(u'rotmic_dnacomponent_marker')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_dnacomponent', models.ForeignKey(orm['rotmic.dnacomponent'], null=False)),
            ('to_dnacomponent', models.ForeignKey(orm['rotmic.dnacomponent'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_dnacomponent_id', 'to_dnacomponent_id'])

        # Adding model 'DnaComponentType'
        db.create_table(u'rotmic_dnacomponenttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('subTypeOf', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subTypes', null=True, to=orm['rotmic.DnaComponentType'])),
        ))
        db.send_create_signal('rotmic', ['DnaComponentType'])


    def backwards(self, orm):
        # Deleting model 'Component'
        db.delete_table(u'rotmic_component')

        # Deleting model 'DnaComponent'
        db.delete_table(u'rotmic_dnacomponent')

        # Removing M2M table for field marker on 'DnaComponent'
        db.delete_table(db.shorten_name(u'rotmic_dnacomponent_marker'))

        # Deleting model 'DnaComponentType'
        db.delete_table(u'rotmic_dnacomponenttype')


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
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'Type'", 'to': "orm['rotmic.DnaComponentType']"}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'insert': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'Insert'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'marker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'marker_rel_+'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vectorBackbone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.DnaComponent']", 'null': 'True', 'blank': 'True'})
        },
        'rotmic.dnacomponenttype': {
            'Meta': {'object_name': 'DnaComponentType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'subTypeOf': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTypes'", 'null': 'True', 'to': "orm['rotmic.DnaComponentType']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rotmic']