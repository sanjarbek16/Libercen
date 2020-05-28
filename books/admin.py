from django.contrib import admin
from .models import Book, Favourite, Review, Comment


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'date',)
    list_filter = ('user', 'book',)
    search_fields = ('user', 'book', 'review')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'date')
    list_filters = ('user',)


class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'book')


class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    search_fields = ('name', 'about',)
    prepopulated_fields = {'slug': ('name',),}

admin.site.register(Book, BookAdmin)
admin.site.register(Favourite, FavouriteAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
