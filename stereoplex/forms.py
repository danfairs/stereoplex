from stereoplex.fields import ReCaptchaField
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _

class CommentCaptchaForm(CommentForm):
    recaptcha = ReCaptchaField(
        label=_(u"Stop the Spam!"),
        help_text=_(u"Sorry about this, but I don't want spam comments.")
    )

    def __init__(self, *args, **kwargs):
        super(CommentCaptchaForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = _(u"This won't be published anywhere, it's just in case I need to contact you.")