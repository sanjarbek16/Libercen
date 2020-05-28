from django.contrib import admin
from .models import Post
from .models import Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ('post', 'user',)
    search_fields = ('post',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'post')
    search_fields = ('comment',)

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
