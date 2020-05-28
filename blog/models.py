from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.text import slugify
from datetime import datetime
from django.utils.timezone import now as timezone_now
import os
from django.utils import timezone
from ckeditor.fields import RichTextField

def upload_to(instance, filename):
	now = timezone_now()
	filename_base, filename_ext = os.path.splitext(filename)
	return "images/%s%s" % (
		now.strftime("%Y/%m/%Y%m%d%H%M%S"),
		filename_ext.lower(),)


class Post(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'
    STATUS = (
    (DRAFT, 'Draft'),
    (PUBLISHED, 'Published'),
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, blank=True, null=True)
    author = models.ForeignKey(User, related_name="articles")
    content = RichTextField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    article_image = models.ImageField(upload_to=upload_to, null=True)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)

    class Meta:
    	verbose_name = 'Post'
    	verbose_name_plural = 'Posts'
    	ordering = ('-create_date',)

    def __str__(self):
        return self.title


    def save(self, *args, **kwargs):
        if not self.pk:
            super(Post, self).save(*args, **kwargs)
        else:
            self.update_date = datetime.now()
        if not self.slug:
            slug_str = "%s %s" % (self.pk, self.title.lower())
            self.slug = slugify(slug_str)
        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('post', args=[self.slug])

