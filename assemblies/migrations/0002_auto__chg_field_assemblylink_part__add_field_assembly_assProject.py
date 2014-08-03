# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AssemblyLink.part'
        db.alter_column(u'assemblies_assemblylink', 'part_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assemblies.AssemblyPart']))
        # Adding field 'Assembly.assProject'
        db.add_column(u'assemblies_assembly', 'assProject',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='assemblies', to=orm['assemblies.AssemblyProject']),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'AssemblyLink.part'
        db.alter_column(u'assemblies_assemblylink', 'part_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['assemblies.AssemblyLink']))
        # Deleting field 'Assembly.assProject'
        db.delete_column(u'assemblies_assembly', 'assProject_id')


    models = {
        'assemblies.assembly': {
            'Meta': {'object_name': 'Assembly'},
            'assProject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assemblies'", 'to': "orm['assemblies.AssemblyProject']"}),
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'default': "'gibson'", 'max_length': '30'}),
            'preparedAt': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)'}),
            'preparedBy': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'design'", 'max_length': '30'})
        },
        'assemblies.assemblylink': {
            'Meta': {'ordering': "['assembly', 'position']", 'object_name': 'AssemblyLink'},
            'assembly': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'partLinks'", 'to': "orm['assemblies.Assembly']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['assemblies.AssemblyPart']"}),
            'position': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'assemblies.assemblypart': {
            'Meta': {'object_name': 'AssemblyPart'},
            'assProject': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': "orm['assemblies.AssemblyProject']"}),
            'bioEnd': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'bioStart': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assemblyFragments'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'strand': ('django.db.models.fields.CharField', [], {'default': "'+'", 'max_length': '1'})
        },
        'assemblies.assemblyproject': {
            'Meta': {'object_name': 'AssemblyProject'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'assemblyprojects_authored'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)', 'blank': 'True'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assemblyproject_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'assemblyprojects'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.Project']"}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assemblyproject_created_by'", 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'design'", 'max_length': '30'})
        },
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rotmic.component': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'Component'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'components_authored'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)', 'blank': 'True'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'component_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'components'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.Project']"}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'component_created_by'", 'to': u"orm['auth.User']"})
        },
        'rotmic.dnacomponent': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'DnaComponent', '_ormbases': ['rotmic.Component']},
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.DnaComponentType']", 'on_delete': 'models.PROTECT'}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'genbank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'insert': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_insert_in_dna'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'markers': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'as_marker_in_dna'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.DnaComponent']"}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'planning'", 'max_length': '30'}),
            'translatesTo': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'codingSequences'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['rotmic.ProteinComponent']"}),
            'vectorBackbone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_vector_in_plasmid'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': "orm['rotmic.DnaComponent']"})
        },
        'rotmic.dnacomponenttype': {
            'Meta': {'ordering': "['subTypeOf__name', 'name']", 'object_name': 'DnaComponentType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isInsert': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'subTypeOf': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTypes'", 'null': 'True', 'to': "orm['rotmic.DnaComponentType']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'rotmic.project': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)', 'blank': 'True'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'project_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 8, 3, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_created_by'", 'to': u"orm['auth.User']"})
        },
        'rotmic.proteincomponent': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'ProteinComponent', '_ormbases': ['rotmic.Component']},
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.ProteinComponentType']", 'on_delete': 'models.PROTECT'}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'genbank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'planning'", 'max_length': '30'})
        },
        'rotmic.proteincomponenttype': {
            'Meta': {'ordering': "['subTypeOf__name', 'name']", 'object_name': 'ProteinComponentType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'subTypeOf': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subTypes'", 'null': 'True', 'to': "orm['rotmic.ProteinComponentType']"}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['assemblies']