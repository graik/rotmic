from django.db import models
from django_comments.models import Comment

class RatedComment(Comment):
    CHOICES = ((0, '--'),
               (1, 'fresh'),
               (-1, 'rotten'))
    
    rating = models.IntegerField(choices=CHOICES, default=0)