from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'create_date',)
    list_filter = ('create_date',)
    search_fields = ('title', 'content',)
    prepopulated_fields = {'slug': ('title',),}
    date_hierarchy = 'create_date'
    ordering = ['-create_date']

admin.site.register(Post, PostAdmin)