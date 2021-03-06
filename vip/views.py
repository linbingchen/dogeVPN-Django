# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from vip.models import User
from django.shortcuts import render, render_to_response
from django.forms import ModelForm
from django.core.context_processors import csrf
import time


class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

# Create your views here.


def index(request):
    user_list = User.objects.all()
    context = {	'user_list1': user_list,
                'user_list': user_list,		}
    return render(request, 'vip/index.html', context)


def register(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('vip/register.html', c)


def howtobuy(request):
    return render(request, 'vip/howtobuy.html')


def check_format(request):
    username_str = request.POST["username"]
    password_str = request.POST["password"]
    email_str   = request.POST["email"]
    fg = 1
    if len(username_str) > 0 :
        for tc in username_str:
            if ((ord(tc) >= ord('a') and ord(tc) <=ord('z') ) or (ord(tc) >= ord('A') and ord(tc) <=ord('Z') ) or (ord(tc) >= ord('0') and ord(tc) <=ord('9') ) ):
                pass
            else:
                fg = 0
                break
        if fg == 1 and len(password_str) > 0:
            for tc in password_str:
                if ((ord(tc) >= ord('a') and ord(tc) <=ord('z') ) or (ord(tc) >= ord('A') and ord(tc) <=ord('Z') ) or (ord(tc) >= ord('0') and ord(tc) <=ord('9') )):
                    pass
                else:
                    fg = 0
                    break
        else:
            fg = 0
        
        if fg == 1 and len(email_str) > 0:
            spr_idx = email_str.find('@')
            if spr_idx != -1:
                for i in range(0, spr_idx):
                    tc = email_str[i]
                    if ((ord(tc) >= ord('a') and ord(tc) <=ord('z') ) or (ord(tc) >= ord('A') and ord(tc) <=ord('Z') ) or (ord(tc) >= ord('0') and ord(tc) <=ord('9') )):
                        pass
                    else:
                        fg = 0
                        break
                if fg == 1:
                    for i in range(spr_idx+1,len(email_str)):
                        if ((ord(tc) >= ord('a') and ord(tc) <=ord('z') ) or (ord(tc) >= ord('A') and ord(tc) <=ord('Z') ) or (ord(tc) >= ord('0') and ord(tc) <=ord('9') ) or ord(tc)==ord('.')):
                            pass
                        else:
                            fg = 0
                            break

            else:
                fg = 0
        else:
            fg = 0


    else:
        fg = 0

    return fg


def check_timeout(request):
    try:
        if time.time() - request.session['time'] >= 3000:
            request.session.flush()
            return 1
    except:
        return 2
    return 0


def test(request):

    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        return HttpResponse("You're logged in.")
    else:
        return HttpResponse("Please enable cookies and try again.")
    request.session.set_test_cookie()
    return HttpResponse("")


def check_session(request):
    try:
        exist_user_list = User.objects.all().filter(
            username=request.session['username']).filter(password=request.session['password'])
        if len(exist_user_list) == 0:
            return 0
        else:
            return 1
    except:
        return 0


def edit(request):
    c = {}
    c.update(csrf(request))

    try:
        exist_user_list = User.objects.all().filter(
            username=request.session['username'])
        if len(exist_user_list) != 1:
            context = {'errinf': "异常错误!", 'retlink':"vip:account",}
            return render(request, 'vip/wrong.html', context)
        user = exist_user_list[0]
        c['email'] = user.email
        c['passwd'] = user.password
    except:
        context = {'errinf': "获取用户信息失败!", 'retlink':"vip:account",}
        return render(request, 'vip/wrong.html', context)
    return render_to_response('vip/edit.html', c)


def handledit(request):
    try:
        exist_user_list = User.objects.all().filter(
            username=request.session['username'])
        if len(exist_user_list) != 1:
            context = {'errinf': "异常错误!", }
            return render(request, 'vip/wrong.html', context)
        user = exist_user_list[0]
        user.email = request.POST['email']
        user.password = request.POST['password']
        user.save()
        request.session['password'] = user.password
    except:
        context = {'errinf': "修改失败!",'retlink':"vip:account", }
        return render(request, 'vip/wrong.html', context)

    return account(request)


def login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('vip/login.html', c)


def handlelogin(request):
    # to be continued !!!!!!
    exist_user_list = User.objects.all().filter(
        username=request.POST['username']).filter(password=request.POST['password'])
    if len(exist_user_list) == 0:
        context = {'errinf': "用户名或者密码错误!", 'retlink':"vip:login",}
        return render(request, 'vip/wrong.html', context)

    request.session['username'] = request.POST['username']
    request.session['password'] = request.POST['password']
    request.session['time'] = time.time()

    return account(request)


def account(request):
    if check_timeout(request) != 0 or check_session(request) == 0:
        try:
            request.session.flush()
        except:
            pass
        context = {'errinf': "您还没有登录或者登陆超时!", 
                    'retlink':"vip:login",
        }
        return render(request, 'vip/wrong.html', context)
    exist_user_list = User.objects.all().filter(
        username=request.session['username'])
    if len(exist_user_list) != 1:
        context = {'errinf': "异常错误!", 
                    'retlink':"vip:login",
        }
        return render(request, 'vip/wrong.html', context)
    user = exist_user_list[0]
    context = {'user': user, }
    return render(request, 'vip/account.html', context)


def createuser(request):
    if check_format(request) == 0:
        context = {	'errinf': "注册格式不正确!", 
                    'retlink':"vip:register",
                }
        return render(request, 'vip/wrong.html', context)
    exist_user_list = User.objects.all().filter(
        username=request.POST['username'])
    if len(exist_user_list) != 0:
        context = {	'errinf': "用户已经存在!", 
                    'retlink':"vip:register",
            	}
        return render(request, 'vip/wrong.html', context)

    user = User(username=request.POST['username'], password=request.POST[
                'password'], email=request.POST['email'])
    user.save()
    request.session['username'] = user.username
    request.session['password'] = user.password
    request.session['time'] = time.time()
    return render(request, 'vip/regres.html')
    # return index(request)


def logout(request):
    try:
        request.session.flush()
    except KeyError:
        pass
    context = {'errinf': "退出成功!",
                'retlink':"vip:index",
     }
    return render(request, 'vip/wrong.html', context)

def deposit(request):
    return render(request,'vip/index.html')
