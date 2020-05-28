from books.models import Book, Review
from rest_framework import viewsets
from api.serializers import BookSerializer, ReviewSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Book.objects.all().order_by('name')
    serializer_class = BookSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Review.objects.all().order_by('-date')
    serializer_class = ReviewSerializer
