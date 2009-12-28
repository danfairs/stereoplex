from django.contrib import admin
from basic.blog.admin import PostAdmin
from basic.blog.models import Post
from tinymce.widgets import TinyMCE

class TinyPostAdmin(PostAdmin):
    
    def formfield_for_dbfield(self, db_field, **kwargs):        
        if db_field.name == 'body':
            return db_field.formfield(widget=TinyMCE(
                attrs={'cols': 80, 'rows': 30},
                mce_attrs={
                    'theme': 'advanced', 
                    'skin': 'stereoplex',
                    'plugins': "safari,style,layer,table,save,advhr,advimage,advlink,emotions,inlinepopups,insertdatetime,preview,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
                    'theme_advanced_buttons1' : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
                    'theme_advanced_buttons2' : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
                    'theme_advanced_buttons3' : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
                    'theme_advanced_buttons4' : "insertlayer,moveforward,movebackward,absolute,|,styleprops,spellchecker,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,blockquote,pagebreak,|,insertfile,insertimage",
                    'theme_advanced_toolbar_location' : "top",
                    'theme_advanced_toolbar_align' : "left",
                    'theme_advanced_statusbar_location' : "bottom",
                    'theme_advanced_resizing' : True,                    
                    },
            ))
        return super(TinyPostAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
admin.site.unregister(Post)
admin.site.register(Post, TinyPostAdmin)


