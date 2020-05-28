from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import UserEditForm, ProfileForm
from .models import Profile, Contact
from common.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse_lazy
from activities.views import actions_list
from posts.models import Post


# view to show welcome page or feed
def home(request):
    if request.user.is_authenticated():
        return actions_list(request)
    else:
        return render(request, 'basic/welcome.html')


def profile_info(request, username):
    page_user = get_object_or_404(User, username=username)
    info = 'info'
    return render(request, 'users/profile.html', {'page_user':page_user, 'info':info})


# main profile page
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=page_user)
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        posts = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'users/posts.html', {'page_user':page_user, 'posts':posts})
    return render(request, 'users/profile-main.html', {'page_user': page_user, 'posts':posts})


def profile_followers(request, username):
    page_user = get_object_or_404(User, username=username)
    followers = page_user.followers.all()
    paginator = Paginator(followers, 20)
    page = request.GET.get('page')
    try:
        followers = paginator.page(page)
    except PageNotAnInteger:
        followers = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        followers = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'users/followers.html', {'page_user':page_user, 'followers':followers})
    return render(request, 'users/profile.html', {'page_user':page_user, 'followers':followers})

    
def profile_following(request, username):
    page_user = get_object_or_404(User, username=username)
    followings = page_user.following.all()
    paginator = Paginator(followings, 20)
    page = request.GET.get('page')
    try:
        followings = paginator.page(page)
    except PageNotAnInteger:
        followings = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        followings = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'users/following.html', {'page_user':page_user, 'followings':followings})
    return render(request, 'users/profile.html', {'page_user':page_user, 'followings':followings})


def profile_fav_books(request, username):
    page_user = get_object_or_404(User, username=username)
    books = page_user.profile.fav_books.all()
    paginator = Paginator(books, 14)
    page = request.GET.get('page')
    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        books = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'users/fav-books.html', {'page_user':page_user, 'books':books})
    return render(request, 'users/profile.html', {'page_user':page_user, 'books':books})


@login_required
def settings(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'users/settings.html', {'profile_form': profile_form, 'user_form':user_form,})










# following other users
@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user,
                                              user_to=user)
                request.user.profile.notify_followed(user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
                request.user.profile.unotify_followed(user)
            return JsonResponse({'status':'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status':'ko'})
    return JsonResponse({'status':'ko'})



'''         
@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.all().exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related('target')
    paginator = Paginator(actions, 12)
    page = request.GET.get('page')
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        actions = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        actions = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,
                      'personal/detail.html',
                      {'section': 'dashboard', 'actions': actions})

    return render(request, 'personal/home.html', {'section': 'dashboard',
                                                      'actions': actions})
                                    

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})
                                                 
                                                 
                                                 
                                 
                                                 
@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request, 'account/user/list.html', {'section': 'people',
                                                      'users': users})
'''


'''
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    if request.user==user:
         return render(request, 'account/user/detail-for-user.html', {'section': 'people', 'user': user})
    else:
          return render(request, 'account/user/detail.html', {'user': user})
'''                                                     
                                                        
                                                 
