from stereoplex.fields import ReCaptchaField
from django.contrib.comments.forms import CommentForm

class CommentCaptchaForm(CommentForm):
    recaptcha = ReCaptchaField()
    