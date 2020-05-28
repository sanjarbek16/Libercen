from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseBadRequest, HttpResponse
from .decorators import ajax_required
import random 
# Create your views here.



# view for rendering all articles with AJAX pagination
def posts(request):
    posts = Post.objects.all().exclude(status=Post.DRAFT)
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'blog/posts.html',
                      {'posts': posts})
    return render(request,
                  'blog/list.html',
                   {'posts': posts,})


# view for rendering post
def post(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.PUBLISHED)
    latest_posts = Post.objects.all().exclude(title=post.title)[:6]
    if len(latest_posts)>4:
        latest_posts = random.sample(list(latest_posts), 3)
    return render(request, 'blog/post.html', {'post':post, 'latest_posts':latest_posts, })
