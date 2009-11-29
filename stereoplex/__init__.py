from threadedcomments.models import ThreadedComment
from stereoplex.forms import ThreadedCommentCaptchaForm

def get_model():
    return ThreadedComment

def get_form():
    return ThreadedCommentCaptchaForm
