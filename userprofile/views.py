from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from .forms import UserLoginForm,UserRegisterForm
from django.contrib.auth.models import User
from .forms import ProfileForm
from .models import Profile
#引入登录验证装饰器
from django.contrib.auth.decorators import login_required
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            #cleaned_data  清晰出合法数据
            data = user_login_form.cleaned_data
            #检查账号，密码是否正确，
            #如果正确返回user对象
            user = authenticate(username=data['username'],password=data['password'])
            if user:
                #将用户数据保存session中，实现了登录动作
                login(request,user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码错误，请重新输入")
        else:
            return HttpResponse("账号密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = {'form':user_login_form}
        return render(request,'userprofile/login.html',context)
    else:
        return HttpResponse("请求错误")


def user_logout(request):
    logout(request)
    return redirect("article:article_list")

def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit = False)
            #设置密码
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            #保存数据立即登录并返回列表页面
            login(request,new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("注册错误，请从新输入")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form':user_register_form}
        return render(request,'userprofile/register.html',context)
    else:
        return HttpResponse("请求错误")

@login_required(login_url='/userprofile/login/')
def user_delete(request,id):
    if request.method == "POST":
        user = User.objects.get(id=id)
        #验证登录用户、等待删除用户是否相同
        if request.user == user:
            #退出登录，删除用户数据并返回
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有相应的权限")
    else:
        return HttpResponse("请求错误")


#编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request,id):
    user = User.objects.get(id=id)
    #user_id 是oneToOneField 自动生成的字段
    # profile = Profile.objects.get(user_id=id)
    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)
    #post请求
    if request.method == 'POST':
        #验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("权限不足")
        profile_form = ProfileForm(request.POST,request.FILES)
        if profile_form.is_valid():
            #取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']
            profile.save()
            #带参数的 redirect()
            return redirect("userprofile:edit",id=id)
        else:
            return HttpResponse("注册输入有误，请从新输入")
    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {'profile_form':profile_form,'profile':profile,'user':user}
        return render(request,'userprofile/edit.html',context)
    else:
        return HttpResponse('请求错误')
