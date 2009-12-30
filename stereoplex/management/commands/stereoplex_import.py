import re
import base64
import datetime
from optparse import make_option
from xml.dom.minidom import parse
from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import transaction
from basic.blog.models import Category
from basic.blog.models import Post
from basic.media.models import Photo
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
        
        # Create all the images
        images = {}
        for image in dom.getElementsByTagName('ATImage'):
            images.update(dict([self.image(image)]))
        
        site = Site.objects.get_current()
        for entry in dom.getElementsByTagName('BlogEntry'):
            post = self.entry(entry, images)
            comments = entry.getElementsByTagName('reply')
            for comment in comments:
                user_id = childElement(comment, 'id')
                submit_date = childDateElement(comment, 'date')
                if user_id == 'danfairs':
                    comment_user = user
                else:
                    comment_user = None
                ct = ContentType.objects.get_for_model(post)
                if not Comment.objects.filter(object_pk=post.pk, content_type=ct, submit_date=submit_date):
                    # cheat, but works
                    comment = Comment(
                        user_name=childElement(comment, 'name'),
                        user=comment_user,
                        comment=childElement(comment, 'text'),
                        content_object=post,
                        site=site,
                        submit_date=submit_date,
                    )
                    comment.save()

    def entry(self, entry, images):
        post, created = Post.objects.get_or_create(slug=childElement(entry, 'id'))
        post.slug = childElement(entry, 'id')
        post.title = childElement(entry, 'title')
        post.tease = childElement(entry, 'description')
        post.publish = childDateElement(entry, 'effectiveDate')
        post.author = self.author
        body = childElement(entry, 'body')
        match = re.search(r'<img.*src=["\']([\w\.]*)["\']', body)
        while match:
            rpl = '<inline type="media.photo" id="%s" class="small_left"' % images[match.groups()[0]]
            body = body[:match.start()] + rpl + body[match.end():] 
            match = re.search(r'<img.*src=["\']([\w\.]*)["\']', body)
        post.body = body
        post.save()

        categories = entry.getElementsByTagName('categories')
        if categories:
            for category_node in categories[0].childNodes:
                text = category_node.childNodes[0].nodeValue.lower()
                category, created = Category.objects.get_or_create(slug=text.lower(), defaults={'title': text})
                post.categories.add(category)
        return post

    def image(self, image):
        image_id = childElement(image, 'id')
        photo, created = Photo.objects.get_or_create(slug=image_id)
        if not created:
            return image_id, photo.pk
        photo.title = childElement(image, 'title')
        photo.description = photo.title
        file_content = ContentFile(base64.b64decode(childElement(image, 'data')))
        photo.photo.save(image_id, file_content)
        photo.save()
        return image_id, photo.pk
        
        
        
        