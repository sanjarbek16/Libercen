from books.models import Book, Review
from rest_framework import serializers


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ('name',
                  'first_published',
                  'publisher',
                  'ISBN',
                  'edition',
                  'page_count',
                  'author',
                  'about',
                  'language',
                  'original_language',
                  'cover',)


class ReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Review
        fields = ('book', 'user', 'review',)