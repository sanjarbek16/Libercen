from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Book, Favourite, Review, Comment
from users.models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import BookForm, ReviewForm
from activities.utils import create_action
from django.db.models import Count
from activities.models import Activity, Action
import json



# book detail page
def detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    reviews = Review.objects.filter(book=book).order_by('-likes')
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)
        if review_form.is_valid():
            new_review = review_form.save(commit=False)
            new_review.book = book
            new_review.user = request.user
            new_review.save()
            messages.success(request, 'Review added successfully')
            create_action(request.user, 'wrote a review', new_review)
            review_form = ReviewForm()
    else:
        review_form = ReviewForm()
        try:
            reviews = paginator.page(page)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            if request.is_ajax():
                return HttpResponse('')
            reviews = paginator.page(paginator.num_pages)
        if request.is_ajax():
            return render(request,
                          'books/detail.html',
                          {'reviews': reviews})

    return render(request, 'books/detail.html', {'book': book, 'reviews':reviews, 'review_form':review_form,})



# adding books to favourites
@ajax_required
@require_POST
@login_required
def add_fav(request):
    action = request.POST.get('action')
    book_id = request.POST.get('id')
    try:
        book = Book.objects.get(id=book_id)
        profile = request.user.profile
        if action == 'fav':
            Favourite.objects.get_or_create(profile=profile, book=book)
        else:
            Favourite.objects.filter(profile=profile, book=book).delete()
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'ko'})
    return JsonResponse({'status': 'ko'})



def list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        books = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        books = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'books/books.html',
                      {'books': books})
    return render(request,
                  'books/list.html',
                   {'books': books,})


@login_required
def book_create(request):
    """
    View for creating a Book.
    """
    if request.method == 'POST':
        # form is sent
        form = BookForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # form data is valid
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            form.save_m2m()
            messages.success(request, 'Book added successfully')
            create_action(request.user, 'added a book', book)
            # redirect to new created item detail view
            return redirect(book.get_absolute_url())
    else:
        # build form with data provided by the bookmarklet via GET
        form = BookForm()

    return render(request, 'books/create.html', {'form': form,})

'''
@ajax_required
@login_required
@require_POST
def review_like(request):
    review_id = request.POST.get('id')
    action = request.POST.get('action')
    if review_id and action:
        try:
            review = Review.objects.get(pk=review_id)
            if action == 'like':
                review.users_like.add(request.user)
                request.user.profile.notify_review_liked(review)
            else:
                review.users_like.remove(request.user)
                #request.user.profile.unotify_liked(post)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ko'})
'''

@login_required
@ajax_required
def review_like(request):
    review_id = request.POST['review']
    review = Review.objects.get(pk=review_id)
    user = request.user
    like = Activity.objects.filter(activity_type=Activity.LIKE, review=review_id,
                                   user=user)
    if like:
        user.profile.unotify_review_liked(review)
        like.delete()

    else:
        like = Activity(activity_type=Activity.LIKE, review=review_id, user=user)
        like.save()
        user.profile.notify_review_liked(review)

    return HttpResponse(review.calculate_likes())

@login_required
@ajax_required
def review_delete(request):
    try:
        review_id = request.POST.get('review')
        review = Review.objects.get(pk=review_id)
        action = Action.objects.get(target_id=review_id)
        if review.user == request.user:
            likes = review.get_likes()
            for like in likes:
                like.delete()
            if action:
                action.delete()
            review.delete()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()

@login_required
@ajax_required
def review_comment(request):
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        review_id = request.POST.get('review')
        review = Review.objects.get(pk=review_id)
        response_data = {}

        comment = Comment(comment=comment_text, user=request.user, review=review,)
        comment.save()

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
        if comment.user == request.user or comment.review.user == request.user:
            comment.delete()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception:
        return HttpResponseBadRequest()