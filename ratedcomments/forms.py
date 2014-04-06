from django import forms
from django_comments.forms import CommentForm
from ratedcomments.models import RatedComment

class RatedCommentForm(CommentForm):
    rating = forms.TypedChoiceField(required=False,
                                    coerce=int,
                                    choices=RatedComment.CHOICES,
                                    initial=0,
                                    empty_value=0)

    def get_comment_model(self):
        # Use our custom comment model instead of the default one.
        return RatedComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(RatedCommentForm, self).get_comment_create_data()
        data['rating'] = self.cleaned_data['rating']
        return data