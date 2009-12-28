from django.contrib import admin
from basic.blog.admin import PostAdmin
from basic.blog.models import Post
from tinymce.widgets import TinyMCE

class TinyPostAdmin(PostAdmin):
    
    def formfield_for_dbfield(self, db_field, **kwargs):        
        if db_field.name == 'body':
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            ))
        return super(TinyPostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
admin.site.unregister(Post)
admin.site.register(Post, TinyPostAdmin)


