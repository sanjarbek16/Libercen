from django import forms
from django.conf import settings
from .models import Post
from ckeditor.widgets import CKEditorWidget


class PostForm(forms.ModelForm):
    post = forms.CharField(label="", widget=CKEditorWidget(attrs={'class':'form-control', 'placeholder':'Start writing here...',}),
                           max_length=4000,
                           required=True)
    class Meta:
        model = Post
        fields = ('post',)
