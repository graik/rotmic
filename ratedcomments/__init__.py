from ratedcomments.models import RatedComment
from ratedcomments.forms import RatedCommentForm

def get_model():
    return RatedComment

def get_form():
    return RatedCommentForm
