from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Task, Comment

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserRoleForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)
    
    class Meta:
        model = User
        fields = ('role',)

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'assigned_to', 'status']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if user and not user.groups.filter(name='Admin').exists():
            self.fields.pop('assigned_to')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a comment...'}),
        }

class TaskFilterForm(forms.Form):
    FILTER_CHOICES = [
        ('', 'All'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    PRIORITY_CHOICES = [
        ('', 'All'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    status = forms.ChoiceField(choices=FILTER_CHOICES, required=False)
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    assigned_to = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label="All Users")
    search = forms.CharField(required=False) 