import datetime
from optparse import make_option
from xml.dom.minidom import parse
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import transaction
from basic.blog.models import Post
from tagging.models import Tag

months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

def childElement(parent, element_name):
    for child in parent.childNodes:
        if child.nodeName == element_name:
            return child.childNodes[0].nodeValue
    # Heuristic, look deeper
    pot = parent.getElementsByTagName(element_name)
    if len(pot) != 1:
        raise ValueError
    try:
        return pot[0].childNodes[0].nodeValue
    except IndexError:
        return ''
    
def childDateElement(parent, element_name):
    date_text = childElement(parent, element_name)
    _, day, month_name, year, time, _ = date_text.split()
    hour, minute, second = time.split(':')
    month = months.index(month_name.lower()) + 1
    if month < 1:
        raise ValueError
        
    return datetime.datetime(int(year), month, int(day), int(hour), int(minute), int(second), 0)

class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', help='Import file name', dest='file'),
    )
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='dan')
        except User.DoesNotExist:
            user = User.objects.create_user('dan', 'dan@stereoplex.com')
        self.author = user
        dom = parse(options['file'])
        
        site = Site.objects.get_current()
        for entry in dom.getElementsByTagName('BlogEntry'):
            post = self.entry(entry)
            comments = entry.getElementsByTagName('reply')
            for comment in comments:
                user_id = childElement(comment, 'id')
                submit_date = childDateElement(comment, 'date')
                if user_id == 'danfairs':
                    comment_user = user
                else:
                    comment_user = None
                comment = Comment(
                    user_name=childElement(comment, 'name'),
                    user=comment_user,
                    comment=childElement(comment, 'text'),
                    content_object=post,
                    site=site,
                    submit_date=submit_date,
                )
                comment.save()
                    
            
    def entry(self, entry):
        post, created = Post.objects.get_or_create(slug=childElement(entry, 'id'))
        if not created:
            return post
        post.slug = childElement(entry, 'id')
        post.title = childElement(entry, 'title')
        post.teaser = childElement(entry, 'description')
        post.publish = childDateElement(entry, 'effectiveDate')
        post.author = self.author
        post.body = childElement(entry, 'body')
        post.save()
        return post

        
        
        
        
        