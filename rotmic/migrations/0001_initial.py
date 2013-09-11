# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ComponentAttachment'
        db.create_table(u'rotmic_componentattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('f', self.gf('rotmic.utils.filefields.DocumentModelField')(max_length=100, extensions=())),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['rotmic.Component'])),
        ))
        db.send_create_signal('rotmic', ['ComponentAttachment'])

        # Adding model 'Component'
        db.create_table(u'rotmic_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='component_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 9, 11, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='component_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 9, 11, 0, 0))),
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
            ('componentType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rotmic.DnaComponentType'])),
            ('insert', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='as_insert_in_dna+', null=True, to=orm['rotmic.DnaComponent'])),
            ('vectorBackbone', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='as_vector_in_plasmid', null=True, to=orm['rotmic.DnaComponent'])),
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

        # Adding model 'CellComponent'
        db.create_table(u'rotmic_cellcomponent', (
            (u'component_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['rotmic.Component'], unique=True, primary_key=True)),
            ('componentType', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rotmic.CellComponentType'])),
            ('plasmid', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='as_plasmid_in_cell', null=True, to=orm['rotmic.DnaComponent'])),
        ))
        db.send_create_signal('rotmic', ['CellComponent'])

        # Adding M2M table for field marker on 'CellComponent'
        m2m_table_name = db.shorten_name(u'rotmic_cellcomponent_marker')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('cellcomponent', models.ForeignKey(orm['rotmic.cellcomponent'], null=False)),
            ('dnacomponent', models.ForeignKey(orm['rotmic.dnacomponent'], null=False))
        ))
        db.create_unique(m2m_table_name, ['cellcomponent_id', 'dnacomponent_id'])

        # Adding model 'DnaComponentType'
        db.create_table(u'rotmic_dnacomponenttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('subTypeOf', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subTypes', null=True, to=orm['rotmic.DnaComponentType'])),
            ('isInsert', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rotmic', ['DnaComponentType'])

        # Adding model 'CellComponentType'
        db.create_table(u'rotmic_cellcomponenttype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('subTypeOf', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subTypes', null=True, to=orm['rotmic.CellComponentType'])),
            ('hasPlasmids', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('rotmic', ['CellComponentType'])


    def backwards(self, orm):
        # Deleting model 'ComponentAttachment'
        db.delete_table(u'rotmic_componentattachment')

        # Deleting model 'Component'
        db.delete_table(u'rotmic_component')

        # Deleting model 'DnaComponent'
        db.delete_table(u'rotmic_dnacomponent')

        # Removing M2M table for field marker on 'DnaComponent'
        db.delete_table(db.shorten_name(u'rotmic_dnacomponent_marker'))

        # Deleting model 'CellComponent'
        db.delete_table(u'rotmic_cellcomponent')

        # Removing M2M table for field marker on 'CellComponent'
        db.delete_table(db.shorten_name(u'rotmic_cellcomponent_marker'))

        # Deleting model 'DnaComponentType'
        db.delete_table(u'rotmic_dnacomponenttype')

        # Deleting model 'CellComponentType'
        db.delete_table(u'rotmic_cellcomponenttype')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rotmic.cellcomponent': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'CellComponent', '_ormbases': ['rotmic.Component']},
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.CellComponentType']"}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'as_marker_in_cell'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.DnaComponent']"}),
            'plasmid': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_plasmid_in_cell'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"})
        },
        'rotmic.cellcomponenttype': {
            'Meta': {'object_name': 'CellComponentType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'hasPlasmids': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'subTypeOf': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTypes'", 'null': 'True', 'to': "orm['rotmic.CellComponentType']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'rotmic.component': {
            'Meta': {'object_name': 'Component'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 11, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'component_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 11, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'component_created_by'", 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'planning'", 'max_length': '30'})
        },
        'rotmic.componentattachment': {
            'Meta': {'object_name': 'ComponentAttachment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'f': ('rotmic.utils.filefields.DocumentModelField', [], {'max_length': '100', 'extensions': '()'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['rotmic.Component']"})
        },
        'rotmic.dnacomponent': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'DnaComponent', '_ormbases': ['rotmic.Component']},
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.DnaComponentType']"}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'insert': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_insert_in_dna+'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'marker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'as_marker_in_dna'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.DnaComponent']"}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vectorBackbone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_vector_in_plasmid'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"})
        },
        'rotmic.dnacomponenttype': {
            'Meta': {'object_name': 'DnaComponentType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInsert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'subTypeOf': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTypes'", 'null': 'True', 'to': "orm['rotmic.DnaComponentType']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['rotmic']