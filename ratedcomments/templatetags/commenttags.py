from django.utils.safestring import mark_safe
from django import template
import django.utils.html as html
import django.db.models as models

import ratedcomments.models as CM
import django.contrib.contenttypes.models as CT
import django.contrib.staticfiles.templatetags.staticfiles as ST



register = template.Library()

@register.filter(name='restyle')
def restyle(field, css):
    """
    from: http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/
    Add additional CSS or style tags to a django-rendered field directly in template.
    
    Usage: {{ form.field | restyle:"text-align:right" }}
    """
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            t, v = d.split(':')
            attrs[t] = v
            
    return field.as_widget(attrs=attrs)


@register.assignment_tag
def recentcomments(n=10):
    qs = CM.RatedComment.objects.filter(
            is_removed = False,
        )
    return qs.order_by('-submit_date')[:n]


def get_comments(obj):
    """all comments associated to obj"""
    ct = CT.ContentType.objects.get_for_model(obj._meta.model)
    comments = CM.RatedComment.objects.filter(content_type__pk=ct.id,
                                              object_pk=obj.id,
                                              is_removed=False)
    return comments

def comment_vote_count(obj):
    """
    Return number of rotten, fresh, neutral (no rating)
    @return dict - {'rotten':int, 'fresh':int, 'neutral':int}
    """
    d = {'fresh':0, 'rotten':0, 'neutral':0, 'comments':[]}
    
    comments = get_comments(obj)
    d['comments'] = comments

    if comments.count() == 0:
        return d
    
    d['neutral'] = comments.filter(rating=0).count()
    d['fresh'] = comments.filter(rating=1).count()
    d['rotten'] = comments.filter(rating=-1).count()
    
    return d

def comment_vote_stats(obj):
    """@return dict"""
    votes = comment_vote_count(obj)
    total = votes['fresh'] + votes['rotten'] + votes['neutral']

    verdict = 'neutral'
    percent = 0
    
    if votes['fresh'] + votes['rotten'] > 0:
        percent = 100. * votes['fresh'] / (votes['fresh'] + votes['rotten'])
        if percent > 65:
            verdict = 'fresh'
        elif percent < 35:
            verdict = 'rotten'
        else:
            verdict = 'mixed'
    
    votes.update({'total':total, 'verdict':verdict, 'percent':percent})
    return votes
    

@register.filter(is_safe=True)
def comment_vote_symbol(obj, height=0, iconset=None, mouseover=''):
    """
    Image summary of comment ratings associated with an object.
    Image annotated with % of fresh votes in title(mouseover)
    """
    icons = iconset or {'rotten': 'rotten.png',
                        'fresh': 'fresh.png', 
                        'mixed': 'mixed.png',
                        'neutral': 'comment.png'}
    
    votes = comment_vote_stats(obj)
    verdict = votes['verdict']
    
    attrs = 'height="%i"' % height if height else ''
    img = '<img src="%s" %s title="%s">'
    f = ST.static( icons[ verdict ] )
    
    title = '%(total)i comments' % votes
    if verdict != 'neutral':
        title = """%(verdict)s! score: %(percent)i%%
comments
fresh: %(fresh)i | rotten: %(rotten)i | no rating: %(neutral)i""" % votes
        
    title = mouseover or title
    return mark_safe(img % (f, attrs, title) )


@register.filter(is_safe=True)
def comment_vote_symbol_micro(obj, height=0, mouseover=''):
    """Image annotated with % of fresh votes in title(mouseover)"""
    icons = {'rotten': 'rotten_nano.png',
             'fresh': 'fresh_nano.png', 
             'mixed': 'mixed_nano.png',
             'neutral': 'comment.png'}
    return comment_vote_symbol(obj, height=height, iconset=icons, 
                               mouseover=mouseover)


@register.filter(is_safe=True)
def comment_vote_score(obj, height=25, url='#comments'):
    """
    Text summary and score of comments associated to obj
    """
    votes = comment_vote_stats(obj)
    votes.update( {'url':url, 'heigth':height} )
    votes['plural'] = '' if votes['total'] == 1 else 's'
    
    r = """
    <b>%(verdict)s!</b> score: <b>%(percent)i%%</b><br>
        <a href="%(url)s">%(total)i comment%(plural)s:</a><br>
    <small>
        fresh: %(fresh)i | rotten: %(rotten)i | no rating: %(neutral)i
    </small>
    """  % votes
    
    if votes['verdict'] == 'neutral':  ## no votes were cast
        r = '<a href="%(url)s">%(total)i comment%(plural)s</a>' % votes
    
    return mark_safe(r)


def comment_info_icon(obj, height=0, url=''):
    """
    Display icon depending on comment status. None if there are no comments.
    Mouseover contains rating summary **and** all the comments.
    """
    votes = comment_vote_stats(obj)
    votes['plural'] = '' if votes['total'] == 1 else 's'
    comments = votes['comments']
    
    if not comments.count():
        return ''

    title = ''
    if votes['verdict'] != 'neutral':
        title += '%(verdict)s!\n' % votes
        title += 'fresh: %(fresh)i | rotten: %(rotten)i | no rating: %(neutral)i\n'\
            % votes

    title += '%(total)i comment%(plural)s:\n\n' % votes
    title += '\n-----------------\n'.join(\
        [unicode(c.user_name) + ': ' + c.comment for c in comments])
        
    url = url or obj.get_absolute_url() + '#comments'
    img = comment_vote_symbol_micro(obj, height=height, mouseover=title)

    r = '<a href="%s">%s</a>' % (url, img)
        
    return mark_safe(r)
