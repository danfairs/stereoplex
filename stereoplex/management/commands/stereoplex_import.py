import datetime
from optparse import make_option
from xml.sax import parse
from xml.sax.handler import ContentHandler
from django.core.management import BaseCommand
from django.db import transaction
from basic.blog.models import Post
from tagging.models import Tag

class Ignore(object):
    pass
    
class Stack(list):
    push = list.append
    def peek(self):
        return self[-1]

class Category(object):
    def __init__(self, name):
        self.name = name

class Image(object):
    pass

class Discussion(object):
    pass
    
class Reply(object):
    pass
    
class Creator(object):
    pass

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


class ApplierStack(Stack):
    
    def apply(self):
        while self:
            applier = self.pop()
            applier.apply()

    def push(self, context, attribute=None, applier_class=Applier):
        if attribute:
            applier = applier_class(context, attribute)
        else:
            applier = context
        return super(ApplierStack, self).push(applier)
        
class DateApplier(Applier):
    
    def apply(apply):
        setattr(self.context, self.attribute, datetime.datetime(self.text[0]))
        
        
class TagApplier(object):
    def __init__(self, context):
        self.context = context
        
    def append(self, tag):
        self.tag = tag
        
    def apply(self):
        try:
            self.context.save()
            Tag.objects.add_tag(self.context, self.tag)
        except AttributeError:
            # The object wasn't taggable
            pass
                

class StereoplexHandler(ContentHandler):

    ignored_elements = [
        'excludeFromNav',
        'relatedItems',
        'displayMode',
        'displayItems',
        'warnForUnpublishedEntries',
        'allowCrossPosting',
        'crossPosts',
        'alwaysOnTop',
        'contributors',
        'creators',
        'language',
        'rights',
        'creation_date',
        'modification_date',
        'filename',
    ]

    debug = False

    def __init__(self):
        ContentHandler.__init__(self)
        self.stack = Stack()
        self.appliers = ApplierStack()

    def startElement(self, name, attrs):
        name = clean(name)
        if name not in self.ignored_elements:
            getattr(self, 'start_%s' % name)(attrs)
        
    def endElement(self, name):
        name = clean(name)
        if name not in self.ignored_elements:
            getattr(self, 'end_%s' % name, lambda: 1)()
            
    def characters(self, content):
        self.appliers[-1].append(content)
        
    def start_Blog(self, attrs):
        self.stack.push(Ignore())
        
    def end_Blog(self):
        blog = self.stack.pop()
        self.appliers.apply()
    
    def start_id(self, attrs):
        self.appliers.push(self.stack.peek(), 'slug')
    
    def start_title(self, attrs):
        self.appliers.push(self.stack.peek(), 'title')
    
    def start_subject(self, attrs):
        pass
        
    def start_description(self, attrs):
        self.appliers.push(self.stack.peek(), 'tease')
            
    def start_creators(self, attrs):
        raise NotImplementedError
            
    def start_sequence_item(self, attrs):
        self.appliers.push(TagApplier(self.stack.peek()))
            
    def start_effectiveDate(self, attrs):
        self.appliers.push(self.stack.peek(), 'publish')
        
    def start_categories(self, attrs):
        pass
        
    def start_BlogEntry(self, attrs):
        self.stack.push(Post())
        
    def end_BlogEntry(self):
        entry = self.stack.pop()
        self.appliers.apply()
        entry.save()
        print "Saved %s" % entry.title
        
    def start_body(self, attrs):
        self.appliers.push(self.stack.peek(), 'body')

    def start_SyndicationInformation(self, attrs):
        self.stack.push(Ignore())
        
    def end_SyndicationInformation(self):
        self.stack.pop()
        self.appliers.apply()
    
    def start_ATImage(self, attrs):
        self.stack.push(Image())
        
    def end_ATImage(self):
        image = self.stack.pop()
        self.appliers.apply()
        # TODO rewrite the body to refer to the image
        
        
        
    def start_content_type(self, attrs):
        self.appliers.push(self.stack.peek(), 'content_type')
        
    def start_data(self, attrs):
        self.appliers.push(self.stack.peek(), 'data')
        
    def start_discussion(self, attrs):
        self.stack.push(Discussion())
        
    def end_discussion(self):
        self.stack.pop()
        self.appliers.apply()
        # TODO save
    
    def start_reply(self, attrs):
        self.stack.push(Reply())
        
    def end_reply(self):
        self.stack.pop()
        # TODO save
        
    def start_creator(self, attrs):
        self.stack.push(Creator())
        
    def end_creator(self):
        self.stack.pop()
        self.appliers.apply()
        
        # TODO save
        
    def start_text(self, attrs):
        self.appliers.push(self.stack.peek(), 'comment')
        
    def start_date(self, attrs):
        self.appliers.push(self.stack.peed(), 'date', applier_class=DateApplier)
        
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
        
        
        