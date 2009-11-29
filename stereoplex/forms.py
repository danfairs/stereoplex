from stereoplex import fields
from threadedcomments.forms import ThreadedCommentForm

class ThreadedCommentCaptchaForm(ThreadedCommentForm):
    recaptcha = fields.ReCaptchaField()
    
