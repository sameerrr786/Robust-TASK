from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseForbidden

from .models import Task, Comment
from .forms import SignUpForm, TaskForm, CommentForm, TaskFilterForm, UserRoleForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        role_form = UserRoleForm(request.POST)
        
        if form.is_valid() and role_form.is_valid():
            user = form.save()
            group = role_form.cleaned_data['role']
            user.groups.add(group)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
        role_form = UserRoleForm()
    
    return render(request, 'registration/signup.html', {'form': form, 'role_form': role_form})

@login_required
def dashboard(request):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    # Admin stats
    if is_admin:
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        pending_tasks = Task.objects.filter(status='pending').count()
        in_progress_tasks = Task.objects.filter(status='in_progress').count()
        
        tasks_by_priority = {
            'high': Task.objects.filter(priority='high').count(),
            'medium': Task.objects.filter(priority='medium').count(),
            'low': Task.objects.filter(priority='low').count(),
        }
        
        users_with_task_count = User.objects.annotate(
            task_count=Count('assigned_tasks')
        ).order_by('-task_count')[:5]
        
        context = {
            'is_admin': True,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'tasks_by_priority': tasks_by_priority,
            'users_with_task_count': users_with_task_count
        }
    else:
        # User stats
        user_tasks = Task.objects.filter(assigned_to=user)
        total_tasks = user_tasks.count()
        completed_tasks = user_tasks.filter(status='completed').count()
        pending_tasks = user_tasks.filter(status='pending').count()
        context = {
            'is_admin': False,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
        }
        
    return render(request, 'todo_app/dashboard.html', context)

@login_required
def task_list(request):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    if is_admin:
        tasks = Task.objects.all().order_by('-created_at')
    else:
        tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')
    
    filter_form = TaskFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data['status']
        priority = filter_form.cleaned_data['priority']
        assigned_to = filter_form.cleaned_data['assigned_to']
        search = filter_form.cleaned_data['search']
        
        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if assigned_to and is_admin:
            tasks = tasks.filter(assigned_to=assigned_to)
        if search:
            tasks = tasks.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
    
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'is_admin': is_admin,
    }
    
    return render(request, 'todo_app/task_list.html', context)

@login_required
def task_detail(request, task_id):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    task = get_object_or_404(Task, pk=task_id)
    
    # Check if user has permission to view this task
    if not is_admin and task.assigned_to != user:
        return HttpResponseForbidden("You don't have permission to view this task")
    
    comments = task.comments.all().order_by('created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        comment_form = CommentForm()
    
    context = {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'is_admin': is_admin,
    }
    
    return render(request, 'todo_app/task_detail.html', context)

@login_required
def create_task(request):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    if not is_admin:
        return HttpResponseForbidden("You don't have permission to create tasks")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, user=user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(user=user)
    
    return render(request, 'todo_app/task_form.html', {
        'form': form,
        'is_create': True,
    })

@login_required
def edit_task(request, task_id):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    task = get_object_or_404(Task, pk=task_id)
    
    if not is_admin:
        return HttpResponseForbidden("You don't have permission to edit tasks")
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, user=user)
    
    return render(request, 'todo_app/task_form.html', {
        'form': form,
        'task': task,
        'is_create': False,
    })

@login_required
def delete_task(request, task_id):
    user = request.user
    is_admin = user.groups.filter(name='Admin').exists()
    
    if not is_admin:
        return HttpResponseForbidden("You don't have permission to delete tasks")
    
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    
    return render(request, 'todo_app/task_confirm_delete.html', {'task': task})

@login_required
def update_task_status(request, task_id):
    user = request.user
    task = get_object_or_404(Task, pk=task_id)
    
    # Check if user has permission to update this task
    is_admin = user.groups.filter(name='Admin').exists()
    if not is_admin and task.assigned_to != user:
        return HttpResponseForbidden("You don't have permission to update this task")
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [choice[0] for choice in Task.STATUS_CHOICES]:
            task.status = new_status
            task.save()
            messages.success(request, f'Task status updated to {dict(Task.STATUS_CHOICES)[new_status]}')
        
        return redirect(request.POST.get('next', reverse('task_list')))
    
    return redirect('task_detail', task_id=task.id)
