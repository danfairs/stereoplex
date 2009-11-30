import datetime
from optparse import make_option
from xml.dom.minidom import parse
from django.core.management import BaseCommand
from django.db import transaction
from basic.blog.models import Post
from tagging.models import Tag


class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', help='Import file name', dest='file'),
    )
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        dom = parse(options['file'])
        for entry in dom.getElementsByTagName('BlogEntry'):
            self.entry(entry)
            
    def entry(self, entry):
        pass
        
        
        
        
        