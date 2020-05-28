from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest,\
                        HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from common.decorators import ajax_required
from activities.utils import create_action
from activities.models import Action, Notification
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User


@login_required
def actions_list(request):
    actions = Action.objects.exclude(user=request.user, target_id=None)
    users = User.objects.filter(is_staff=True)
    following_ids = request.user.following.values_list('id', flat=True)
    page = request.GET.get('page')
    actions = actions.filter(user_id__in=following_ids).select_related('user', 'user__profile').prefetch_related('target')
    paginator = Paginator(actions, 12)
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        actions = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        actions = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'actions/partial_action.html', {'actions': actions})
    return render(request, 'actions/main.html', {'actions': actions, 'users':users })
    #from_feed = -1
    #if feeds:
    #    from_feed = feeds[0].id
    #return render(request, 'feeds/main.html', {
     #   'feeds': feeds,
      #  'from_feed': from_feed,
       # 'page': 1,
        #})



@login_required
def notifications(request):
    user = request.user
    notifications = Notification.objects.filter(to_user=user)
    unread = Notification.objects.filter(to_user=user, is_read=False)
    for notification in unread:
        notification.is_read = True
        notification.save()

    return render(request, 'activities/notifications.html',
                  {'notifications': notifications})


@login_required
@ajax_required
def last_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(to_user=user,
                                                is_read=False)
    for notification in notifications:
        notification.is_read = True
        notification.save()

    return render(request,
                  'activities/last_notifications.html',
                  {'notifications': notifications})


@login_required
@ajax_required
def check_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(to_user=user,
                                                is_read=False)
    return HttpResponse(len(notifications))