from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from typing import Dict, Any

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')

@login_required
def topics(request: HttpRequest) -> HttpResponse:
    """显示所有的主题"""
    # topics = Topic.objects.order_by('date_added')
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """显示单个主题及其所有的条目"""
    topic = get_object_or_404(Topic.objects.prefetch_related('entries'), id=topic_id, owner=request.user)
    # 确认请求的主题属于当前用户
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')

    context = {'topic':topic, 'entries':entries}
    return render(request, 'learning_logs/topic.html', context)

@login_required
def new_topic(request):
    """添加新主题"""
    if request.method != 'POST':
        # 未提交数据：创建一个新表单
        form = TopicForm()
    else:
        # POST 提交的数据，对数据进行处理
        form = TopicForm(request.POST)
        if form.is_valid():
            new_topic = form.save()
            new_topic.owner = request.user
            new_topic.save()
            messages.success(request, f'主题“{new_topic.text}”已创建成功！')
            return HttpResponseRedirect(reverse('learning_logs:topics'))

    context = {'form':form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """在特定的主题中添加新条目"""
    topic = get_object_or_404(Topic, id=topic_id, owner=request.user)

    if request.method == 'POST':
        # POST提交的数据，对数据进行处理
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            messages.success(request, '条目已添加成功！')
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic_id]))
    else:
        # 未提交数据，创建一个空表单
        form = EntryForm()

    context = {'topic':topic, 'form':form}
    return render(request, 'learning_logs/new_entry.html', context) 

@login_required
def edit_entry(request, entry_id):
    """编辑既有条目"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        messages.error(request, '您没有权限编辑此条目')
        return redirect('learning_logs:topics')
    
    if request.method == "POST":
        # POST 提交的数据，对数据进行处理
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '条目已更新成功')
            return HttpResponseRedirect(reverse('learning_logs:topic', args=[topic.id]))
    else:
        # 初次请求，使用当前条目填充表单
        form = EntryForm(instance=entry)
        
        
    context = {'entry':entry, 'topic':topic, 'form':form}
    return render(request, 'learning_logs/edit_entry.html', context)
