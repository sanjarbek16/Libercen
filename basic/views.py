from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from common.decorators import ajax_required



# Welcome page view
def welcome(request):
    return render(request, 'basic/welcome.html',)


# privacy policy
def policy(request):
    return render(request, 'basic/privacy-policy.html',)    

@login_required
@ajax_required
def user_menu(request):
    user = request.user

    return render(request,
                  'basic/user_menu.html',
                  {'user': user})