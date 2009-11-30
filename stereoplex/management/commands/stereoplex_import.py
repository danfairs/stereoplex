from optparse import make_option
from xml.sax import parse
from xml.sax.handler import ContentHandler
from django.core.management import BaseCommand
from django.db import transaction
from basic.blog.models import Post

def skip_blog(func):
    def wrapped(self, *args, **kwargs):
        ob = self.stack[-1]
        if ob is None:
            return
        func(self, *(args + (ob,)), **kwargs)
    return wrapped

def clean(v):
    return v.replace('-', '_')


class Applier(object):
    
    text = []
    
    def __init__(self, context, attribute):
        self.context = context
        self.attribute = attribute
        
    def append(self, text):
        self.text.append(text)
        
    def apply(self):
        setattr(self.context, self.attribute, ''.join(self.text))
        
    def __repr__(self):
        return u'<Applier for %s %s = %s' % (self.context.__class__, self.attribute, ''.join(self.text))
                

class StereoplexHandler(ContentHandler):

    ignored_elements = [
        'excludeFromNav',
        'relatedItems',
        'displayMode',
        'displayItems',
        'warnForUnpublishedEntries',
        'allowCrossPosting',
        'crossPosts',
    ]

    def __init__(self):
        ContentHandler.__init__(self)
        self.stack = []

    def startElement(self, name, attrs):
        name = clean(name)
        if name not in self.ignored_elements:
            getattr(self, 'start_%s' % name)(attrs)
        
    def endElement(self, name):
        name = clean(name)
        if name not in self.ignored_elements:
            getattr(self, 'end_%s' % name)()
        
    @skip_blog
    def characters(self, content, ob):
        ob.append(content)
        
    def start_Blog(self, attrs):
        self.stack.append(None)
        
    @skip_blog
    def start_id(self, attrs, ob):
        raise NotImplementedError

    @skip_blog
    def end_id(self, ob):
        raise NotImplementedError

    @skip_blog
    def start_title(self, attrs, ob):
        raise NotImplementedError

    @skip_blog
    def end_title(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_subject(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_subject(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_description(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_description(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_contributors(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_contributors(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_creators(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_creators(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_sequence_item(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_sequence_item(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_effectiveDate(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_effectiveDate(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_language(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_language(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_rights(self, attrs, ob):
        raise NotImplementedError
    
    @skip_blog
    def end_rights(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_creation_date(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_creation_date(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_modification_date(self, attrs, ob):
        raise NotImplementedError
        
    @skip_blog
    def end_modification_date(self, ob):
        raise NotImplementedError
        
    @skip_blog
    def start_categories(self, attrs, ob):
        raise NotImplementedError
    
    @skip_blog
    def end_categories(self, ob):
        raise NotImplementedError

    @skip_blog
    def start_BlogEntry(self, attrs, ob):
        self.stack.append(Post())
        
    @skip_blog
    def end_BlogEntry(self, ob):
        entry = self.stack.pop()
        entry.save()
        
    def start_body(self, attrs):
        self.stack.append(Applier(Post(), 'body'))

    def end_body(self):
        import pdb; pdb.set_trace()
        
        body = self.stack.pop()
        body.apply()
        
    
        
class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', help='Import file name', dest='file'),
    )
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        parse(
            options['file'],
            StereoplexHandler()
        )
        
        
        