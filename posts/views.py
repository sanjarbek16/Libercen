from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.decorators import ajax_required
from activities.utils import create_action
from .forms import PostForm
from activities.models import Activity, Action
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from .models import Post, Comment
import json




@login_required
@ajax_required
def post_like(request):
    post_id = request.POST['post']
    post = Post.objects.get(pk=post_id)
    user = request.user
    like = Activity.objects.filter(activity_type=Activity.LIKE, post=post_id,
                                   user=user)
    if like:
        user.profile.unotify_post_liked(post)
        like.delete()

    else:
        like = Activity(activity_type=Activity.LIKE, post=post_id, user=user)
        like.save()
        user.profile.notify_post_liked(post)

    return HttpResponse(post.calculate_likes())


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    return render(request, 'posts/detail.html', {'post': post, })


@login_required
def post_write(request):
    """
    View for writing a Post.
    """
    if request.method == 'POST':
        # form is sent
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # form data is valid
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post written successfully')
            create_action(request.user, 'wrote a post', post)
            # redirect to new created item detail view
            return redirect(post.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = PostForm()

    return render(request, 'posts/write.html', {'form': form,})

@login_required
@ajax_required
def post_delete(request):
    try:
        post_id = request.POST.get('post')
        post = Post.objects.get(pk=post_id)
        action = Action.objects.get(target_id=post_id)
        if post.user == request.user:
            likes = post.get_likes()
            for like in likes:
                like.delete()
            if action:
                action.delete()
            post.delete()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()

@login_required
@ajax_required
def post_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        post_id = request.POST.get('post')
        post = Post.objects.get(pk=post_id)
        response_data = {}

        comment = Comment(comment=comment_text, user=request.user, post=post,)
        comment.save()
        post.user.profile.notify_commented(post)

        response_data['result'] = 'Comment added successfully!'
        response_data['commentpk'] = comment.pk
        response_data['comment'] = comment.comment
        response_data['date'] = comment.date.strftime('%B %d, %Y %I:%M %p')
        response_data['user'] = comment.user.username
        if comment.user.profile.avatar:
            response_data['useravatar'] = comment.user.profile.avatar.url

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@login_required
@ajax_required
def comment_delete(request):
    try:
        comment_id = request.POST.get('comment')
        comment = Comment.objects.get(pk=comment_id)
        post = comment.post
        if comment.user == request.user or comment.post.user == request.user:
            post.user.profile.unotify_commented(post)
            comment.delete()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()
