from django.db import models
from django_comments.models import Comment

from django.utils.safestring import mark_safe
import django.contrib.staticfiles.templatetags.staticfiles as ST

class RatedComment(Comment):
    CHOICES = ((0, '--'),
               (1, 'fresh'),
               (-1, 'rotten'))
    
    rating = models.IntegerField(choices=CHOICES, default=0)

    ICONS = {'rotten': 'rotten.png',
             'fresh': 'fresh.png', 
             'mixed': 'mixed.png',
             'neutral': 'comment.png'}
    
    def get_icon(self, modifier=''):
        """
        @param modifier - str, will be inserted before '.png' file ending
        @return str, fresh/rotten/neutral icon file name
        """
        r = ''
        if self.rating == 0:
            r = self.ICONS['neutral']
        if self.rating == 1:
            r = self.ICONS['fresh']
        if self.rating == -1:
            r = self.ICONS['rotten']
        
        if modifier:
            r = r.replace('.png', modifier+'.png')

        return ST.static(r)
    
    
    def get_icon_html(self, height=0, modifier='_nano'):
        """
        @param height - int, 0..no scaling, otherwise image height
        @return str, HTML snippet for image depending on comment rating
        """
        height = 'height="%i"' % height if height else ''
        r = '<img src="%s" %s>' % (self.get_icon(modifier=modifier), height)
        return mark_safe(r)
    
    