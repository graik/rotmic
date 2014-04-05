## See: http://stackoverflow.com/questions/8771852/how-to-provide-a-delete-button-for-django-built-in-comments-framework

from django.shortcuts import get_object_or_404
import django.http as http
from django_comments.views.moderation import perform_delete
from django_comments.models import Comment

def delete_own_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.user.id != request.user.id and not request.user.is_superuser:
        raise http.Http404('Permission denied')
    perform_delete(request, comment)
    return http.HttpResponseRedirect(comment.content_object.get_absolute_url())