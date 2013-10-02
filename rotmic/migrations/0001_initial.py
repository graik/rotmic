# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'rotmic_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='profile', unique=True, to=orm['auth.User'])),
            ('dcPrefix', self.gf('django.db.models.fields.CharField')(default='mt', max_length=5)),
            ('ccPrefix', self.gf('django.db.models.fields.CharField')(default='mt', max_length=5)),
        ))
        db.send_create_signal('rotmic', ['UserProfile'])

        # Adding model 'ComponentAttachment'
        db.create_table(u'rotmic_componentattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('f', self.gf('rotmic.utils.filefields.DocumentModelField')(max_length=100, extensions=())),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['rotmic.Component'])),
        ))
        db.send_create_signal('rotmic', ['ComponentAttachment'])

        # Adding model 'SampleAttachment'
        db.create_table(u'rotmic_sampleattachment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('f', self.gf('rotmic.utils.filefields.DocumentModelField')(max_length=100, extensions=())),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['rotmic.Sample'])),
        ))
        db.send_create_signal('rotmic', ['SampleAttachment'])

        # Adding model 'Unit'
        db.create_table(u'rotmic_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('unitType', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('conversion', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('rotmic', ['Unit'])

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
            ('allowPlasmids', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allowMarkers', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rotmic', ['CellComponentType'])

        # Adding model 'Component'
        db.create_table(u'rotmic_component', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='component_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='component_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
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
            ('genbank', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
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

        # Adding model 'Location'
        db.create_table(u'rotmic_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='location_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='location_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('displayId', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('temperature', self.gf('django.db.models.fields.FloatField')(default=25.0, null=True, blank=True)),
            ('room', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('rotmic', ['Location'])

        # Adding model 'Rack'
        db.create_table(u'rotmic_rack', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rack_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rack_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('displayId', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='racks', null=True, to=orm['rotmic.Location'])),
        ))
        db.send_create_signal('rotmic', ['Rack'])

        # Adding unique constraint on 'Rack', fields ['displayId', 'location']
        db.create_unique(u'rotmic_rack', ['displayId', 'location_id'])

        # Adding model 'Container'
        db.create_table(u'rotmic_container', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='container_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='container_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('displayId', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('containerType', self.gf('django.db.models.fields.CharField')(default='box', max_length=30)),
            ('rack', self.gf('django.db.models.fields.related.ForeignKey')(related_name='containers', to=orm['rotmic.Rack'])),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('rotmic', ['Container'])

        # Adding unique constraint on 'Container', fields ['displayId', 'rack']
        db.create_unique(u'rotmic_container', ['displayId', 'rack_id'])

        # Adding model 'Sample'
        db.create_table(u'rotmic_sample', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('registeredBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sample_created_by', to=orm['auth.User'])),
            ('registeredAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('modifiedBy', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sample_modified_by', null=True, to=orm['auth.User'])),
            ('modifiedAt', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('displayId', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(related_name='samples', to=orm['rotmic.Container'])),
            ('aliquotNr', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='ok', max_length=30)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('preparedAt', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2013, 10, 2, 0, 0))),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('solvent', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('concentration', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('concentrationUnit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='concUnit+', null=True, to=orm['rotmic.Unit'])),
            ('amount', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('amountUnit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='amountUnit+', null=True, to=orm['rotmic.Unit'])),
        ))
        db.send_create_signal('rotmic', ['Sample'])

        # Adding model 'DnaSample'
        db.create_table(u'rotmic_dnasample', (
            (u'sample_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['rotmic.Sample'], unique=True, primary_key=True)),
            ('dna', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dna_samples', to=orm['rotmic.DnaComponent'])),
        ))
        db.send_create_signal('rotmic', ['DnaSample'])


    def backwards(self, orm):
        # Removing unique constraint on 'Container', fields ['displayId', 'rack']
        db.delete_unique(u'rotmic_container', ['displayId', 'rack_id'])

        # Removing unique constraint on 'Rack', fields ['displayId', 'location']
        db.delete_unique(u'rotmic_rack', ['displayId', 'location_id'])

        # Deleting model 'UserProfile'
        db.delete_table(u'rotmic_userprofile')

        # Deleting model 'ComponentAttachment'
        db.delete_table(u'rotmic_componentattachment')

        # Deleting model 'SampleAttachment'
        db.delete_table(u'rotmic_sampleattachment')

        # Deleting model 'Unit'
        db.delete_table(u'rotmic_unit')

        # Deleting model 'DnaComponentType'
        db.delete_table(u'rotmic_dnacomponenttype')

        # Deleting model 'CellComponentType'
        db.delete_table(u'rotmic_cellcomponenttype')

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

        # Deleting model 'Location'
        db.delete_table(u'rotmic_location')

        # Deleting model 'Rack'
        db.delete_table(u'rotmic_rack')

        # Deleting model 'Container'
        db.delete_table(u'rotmic_container')

        # Deleting model 'Sample'
        db.delete_table(u'rotmic_sample')

        # Deleting model 'DnaSample'
        db.delete_table(u'rotmic_dnasample')


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
            'Meta': {'ordering': "['subTypeOf__name', 'name']", 'object_name': 'CellComponentType'},
            'allowMarkers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allowPlasmids': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
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
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'component_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
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
        'rotmic.container': {
            'Meta': {'ordering': "('rack', 'displayId')", 'unique_together': "(('displayId', 'rack'),)", 'object_name': 'Container'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'containerType': ('django.db.models.fields.CharField', [], {'default': "'box'", 'max_length': '30'}),
            'displayId': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'container_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'rack': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'containers'", 'to': "orm['rotmic.Rack']"}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'container_created_by'", 'to': u"orm['auth.User']"})
        },
        'rotmic.dnacomponent': {
            'Meta': {'ordering': "['displayId']", 'object_name': 'DnaComponent', '_ormbases': ['rotmic.Component']},
            'componentType': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rotmic.DnaComponentType']"}),
            u'component_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Component']", 'unique': 'True', 'primary_key': 'True'}),
            'genbank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'insert': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_insert_in_dna+'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"}),
            'marker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'as_marker_in_dna'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['rotmic.DnaComponent']"}),
            'sequence': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vectorBackbone': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'as_vector_in_plasmid'", 'null': 'True', 'to': "orm['rotmic.DnaComponent']"})
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
        'rotmic.dnasample': {
            'Meta': {'ordering': "['container', 'displayId']", 'object_name': 'DnaSample', '_ormbases': ['rotmic.Sample']},
            'dna': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dna_samples'", 'to': "orm['rotmic.DnaComponent']"}),
            u'sample_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['rotmic.Sample']", 'unique': 'True', 'primary_key': 'True'})
        },
        'rotmic.location': {
            'Meta': {'ordering': "('displayId',)", 'object_name': 'Location'},
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'location_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'location_created_by'", 'to': u"orm['auth.User']"}),
            'room': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'temperature': ('django.db.models.fields.FloatField', [], {'default': '25.0', 'null': 'True', 'blank': 'True'})
        },
        'rotmic.rack': {
            'Meta': {'ordering': "('location__displayId', 'displayId')", 'unique_together': "(('displayId', 'location'),)", 'object_name': 'Rack'},
            'displayId': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'racks'", 'null': 'True', 'to': "orm['rotmic.Location']"}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rack_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rack_created_by'", 'to': u"orm['auth.User']"})
        },
        'rotmic.sample': {
            'Meta': {'ordering': "['container', 'displayId']", 'object_name': 'Sample'},
            'aliquotNr': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'amountUnit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'amountUnit+'", 'null': 'True', 'to': "orm['rotmic.Unit']"}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'concentration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'concentrationUnit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'concUnit+'", 'null': 'True', 'to': "orm['rotmic.Unit']"}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'samples'", 'to': "orm['rotmic.Container']"}),
            'displayId': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'modifiedBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sample_modified_by'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'preparedAt': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'registeredAt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 2, 0, 0)'}),
            'registeredBy': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sample_created_by'", 'to': u"orm['auth.User']"}),
            'solvent': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'ok'", 'max_length': '30'})
        },
        'rotmic.sampleattachment': {
            'Meta': {'object_name': 'SampleAttachment'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'f': ('rotmic.utils.filefields.DocumentModelField', [], {'max_length': '100', 'extensions': '()'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['rotmic.Sample']"})
        },
        'rotmic.unit': {
            'Meta': {'ordering': "['unitType', 'conversion', 'name']", 'object_name': 'Unit'},
            'conversion': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'unitType': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        'rotmic.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'ccPrefix': ('django.db.models.fields.CharField', [], {'default': "'mt'", 'max_length': '5'}),
            'dcPrefix': ('django.db.models.fields.CharField', [], {'default': "'mt'", 'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['rotmic']