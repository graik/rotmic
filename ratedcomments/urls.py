from django.conf.urls import patterns, include, url

import views as V


urlpatterns = patterns('',
    url(r'^comments/delete_own/(?P<id>.*)/$',V.delete_own_comment, name='delete_own_comment'),
    (r'^comments/', include('django_comments.urls')),
)

