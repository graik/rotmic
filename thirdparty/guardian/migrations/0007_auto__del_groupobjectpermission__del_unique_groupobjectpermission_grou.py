# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.contrib.contenttypes.models import ContentType

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'UserObjectPermission', fields ['user', 'permission', 'object_pk']
        db.delete_unique(u'guardian_userobjectpermission', ['user_id', 'permission_id', 'object_pk'])

        # Removing unique constraint on 'GroupObjectPermission', fields ['group', 'permission', 'object_pk']
        db.delete_unique(u'guardian_groupobjectpermission', ['group_id', 'permission_id', 'object_pk'])

        # Deleting model 'GroupObjectPermission'
        db.delete_table(u'guardian_groupobjectpermission')

        # Deleting model 'UserObjectPermission'
        db.delete_table(u'guardian_userobjectpermission')
        
        ## Manually added: clean up contenttypes
        for content_type in ContentType.objects.filter(app_label='guardian'):
            content_type.delete()


    def backwards(self, orm):
        # Adding model 'GroupObjectPermission'
        db.create_table(u'guardian_groupobjectpermission', (
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('object_pk', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'guardian', ['GroupObjectPermission'])

        # Adding unique constraint on 'GroupObjectPermission', fields ['group', 'permission', 'object_pk']
        db.create_unique(u'guardian_groupobjectpermission', ['group_id', 'permission_id', 'object_pk'])

        # Adding model 'UserObjectPermission'
        db.create_table(u'guardian_userobjectpermission', (
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Permission'])),
            ('object_pk', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'guardian', ['UserObjectPermission'])

        # Adding unique constraint on 'UserObjectPermission', fields ['user', 'permission', 'object_pk']
        db.create_unique(u'guardian_userobjectpermission', ['user_id', 'permission_id', 'object_pk'])


    models = {
        
    }

    complete_apps = ['guardian']