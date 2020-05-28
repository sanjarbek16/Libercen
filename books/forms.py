from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, Review
from ckeditor.widgets import CKEditorWidget



BIRTH_YEAR_CHOICES = ('1980', '1981', '1982','1983', '1984', '1985', '1986', '1987', '1988', '1989','1990', '1991', '1992', '1993',)

'''
class SimpleForm(forms.Form):
    birth_year = forms.DateField(widget=forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES))
    favorite_colors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=FAVORITE_COLORS_CHOICES,
    )
'''

LANGUAGE_CHOICES = ('')

class ReviewForm(forms.ModelForm):
    review = forms.CharField(label="", widget=CKEditorWidget(attrs={'class':'form-control', 'placeholder':'Start writing here...',}),
                             max_length=6000,
                             min_length=200,
                             required=True)
    class Meta:
        model = Review
        fields = ('review',)

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('name',
                  'first_published',
                  'publisher',
                  'ISBN',
                  'edition',
                  'page_count',
                  'author',
                  'genre',
                  'about',
                  'language',
                  'original_language',
                  'cover',)