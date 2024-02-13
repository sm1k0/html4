import datetime
import os.path

from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import *
import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from main.models import Voting, Vote

def check_type(op):
    if op == 1 or op == 2:
        return True
    else:
        return False


def check_list_param(param):
    if len(param) < 2:
        return False
    for i in param:
        print(i)
        if not check_param(i):
            return False
    return True


def check_param(param):
    blacklist = ['{', '}', '[', ']']
    param = param.split()
    param = ''.join(param)
    if len(param) == 0:
        return False
    for i in blacklist:
        if i in param:
            return False
    return True


def get_menu_context():
    return [
        {'url_name': 'index', 'name': 'Главная'},
        {'url_name': 'time', 'name': 'Текущее время'},
    ]


def check_type(op):
    if op == 1 or op == 2:
        return True
    else:
        return False


def check_list_param(param):
    if len(param) < 2:
        return False
    for i in param:
        print(i)
        if not check_param(i):
            return False
    return True


def check_param(param):
    blacklist = ['{', '}', '[', ']']
    param = param.split()
    param = ''.join(param)
    if len(param) == 0:
        return False
    for i in blacklist:
        if i in param:
            return False
    return True


def index_page(request):
    context = {
        'pagename': 'Главная',
        'author': 'Andrew',
        'pages': 4,
        'menu': get_menu_context()
    }
    return render(request, 'pages/index.html', context)


def time_page(request):
    context = {
        'pagename': 'Текущее время',
        'time': datetime.datetime.now().time(),
        'menu': get_menu_context()
    }
    return render(request, 'pages/time.html', context)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'registration/registration.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = {
            'form': self.get_form(),
        }
        return context

    def form_valid(self, form):
        user = form.save()
        profile = Profile()
        profile.bio = ''
        profile.user = user
        profile.logo_image = None
        profile.save()
        login(self.request, user)
        return redirect('index')


class LoginUser(LoginView):
    form_class = LoginPage
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = {
            'form': self.get_form(),
        }
        return context

    def get_success_url(self):
        return reverse_lazy('index')


def logoutUser(request):
    logout(request)
    return redirect('index')


def profile_page(request):
    profile = Profile.objects.get(user=request.user)
    context = {
        'pagename': 'Профиль',
        'menu': get_menu_context(),
        'profile': profile,
        'can_change': True
    }
    return render(request, 'pages/profile.html', context)


def profile_page_id(request, id):
    profile = Profile.objects.get(user=User.objects.get(id=id))
    context = {
        'pagename': 'Профиль',
        'menu': get_menu_context(),
        'profile': profile,
        'can_change': request.user == profile.user
    }
    return render(request, 'pages/profile.html', context)


def votings_page(request):
    context = {
        'votings': Voting.objects.all()
    }
    return render(request, 'votings.html', context)


@login_required(login_url='/login/')
def create_voting_page(request):
    if request.method == 'POST':
        params = dict(request.POST)
        title = params['title'][0].strip()
        text = params['text'][0].strip()
        op = int(params['type'][0])
        options = json.dumps(params['options'])
        if check_param(title) and check_param(text) and check_list_param(params['options']) and check_type(op):
            voting = Voting(title=title, text=text, type=op, options=options, user=request.user)
            voting.save()
            messages.add_message(request, messages.SUCCESS, "Create successfully")
            return redirect(f'/voting/{voting.id}')
        else:
            messages.add_message(request, messages.ERROR, "Some errors")
    return render(request, 'create_voting.html')


def voting_page(request,id):
    voting = Voting.objects.get(id=id)
    vote = Vote.objects.filter(voting=voting)
    comments = Comment.objects.filter(voting=voting)
    options = json.loads(voting.options)
    content = {}
    for i in range(1,len(options)+1):
        if Vote.objects.filter(voting=voting).count() != 0:
            content[i]= int(Vote.objects.filter(voting=voting,option=i).count()/Vote.objects.filter(voting=voting).count()*100)
            content[i] = '{:>4}'.format(content[i])
        else:
            content[i] = 0
    context = {
        'voting': voting,
        'options': options,
        'content': content,
        'comments': comments,
        'creater': voting.user == request.user
        }
    print(content)
    return render(request, 'voting.html', context)

def add_comment(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST' and len(request.POST)>1:
            if request.POST['comment'].strip()!='':
                voting = get_object_or_404(Voting, id=id)
                comment = Comment()
                comment.text = request.POST['comment'].strip()
                comment.user = request.user
                comment.voting = voting
                comment.save()
    else:
        messages.add_message(request, messages.ERROR, "You must be logged in")
    return redirect(f'/voting/{id}')

def add_vote(request,id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            voting = get_object_or_404(Voting, id=id)
            options = json.loads(voting.options)
            can_vote = not bool(Vote.objects.filter(voting=voting,user=request.user).count())
            if can_vote and len(request.POST) > 1:
                params = list(set(dict(request.POST)['option']))
                if voting.type == 1:
                    params = params[:1]
                for i in params:
                    if int(i) in list(range(1, len(options) + 1)):
                        vote = Vote(option=int(i), user=request.user, voting=voting)
                        vote.save()
            else:
                messages.add_message(request, messages.ERROR, "You cannot vote multiple times")
    else:
        messages.add_message(request, messages.ERROR, "You must be logged in")
    return redirect(f'/voting/{id}')

@login_required()
def edit_voting_page(request, id):
    voting = get_object_or_404(Voting, id=id)
    context = {}
    if request.user == voting.user:
        if request.method == 'POST':
            params = dict(request.POST)
            title = params['title'][0].strip()
            text = params['text'][0].strip()
            op = int(params['type'][0])
            options = json.dumps(params['options'])
            if check_param(title) and check_param(text) and check_list_param(params['options']) and check_type(op):
                voting.title = title
                voting.text = text
                voting.type = op
                voting.options = options
                voting.save()
                Vote.objects.filter(voting=voting).delete()
                messages.add_message(request, messages.SUCCESS, 'Editing success')
            else:
                messages.add_message(request, messages.ERROR, 'Editing error')
            return redirect(f'/voting/{voting.id}')

        else:
            context['voting'] = voting
            context['options'] = json.loads(voting.options)
            return render(request, 'edit_voting.html', context)
    else:
        raise PermissionDenied()

@login_required(login_url='/login/')
def delete_voting(request,id):
    voting = get_object_or_404(Voting, id=id)
    if request.user == voting.user:
        voting.delete()
    return redirect('/votings')

@login_required(login_url='/login/')
def edit_profile_page(request):
    context = {
        'imageform': UserLogoForm(),
        'passwordchange': PasswordChangeForm(request.user),
        'biochange': UserBioForm(),
    }
    return render(request, 'edit_profile.html',context)

@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('/edit_profile')

@login_required(login_url='/login/')
def change_bio(request):
    if request.method == 'POST':
        form = UserBioForm(request.POST,instance=Profile.objects.get(user=request.user))
        if form.is_valid():
            form.save()
            messages.success(request, 'Your bio was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('/edit_profile')

@login_required(login_url='/login/')
def change_logoimage(request):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        form = UserLogoForm(request.POST,request.FILES, instance=profile)
        print(request.POST)
        print(request.FILES)
        if form.is_valid():
            if os.path.exists(profile.logo_image.path):
                os.remove(profile.logo_image.path)
            form.save()
            messages.success(request, 'Your logo was successfully updated!')
        else:
            messages.error(request, 'Please correct the error below.')
    return redirect('/edit_profile')
