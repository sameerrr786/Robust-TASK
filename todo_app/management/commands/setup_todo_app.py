from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
import random

from todo_app.models import Task, Comment

class Command(BaseCommand):
    help = 'Sets up initial data for the Todo App'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Setting up Todo App...'))
        
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        user_group, created = Group.objects.get_or_create(name='User')
        
        self.stdout.write(self.style.SUCCESS('Groups created'))
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Admin user created'))
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.SUCCESS('Admin user already exists'))
        
        # Create regular user if it doesn't exist
        if not User.objects.filter(username='user').exists():
            regular_user = User.objects.create_user(
                username='user',
                email='user@example.com',
                password='userpassword'
            )
            regular_user.groups.add(user_group)
            self.stdout.write(self.style.SUCCESS('Regular user created'))
        else:
            regular_user = User.objects.get(username='user')
            self.stdout.write(self.style.SUCCESS('Regular user already exists'))
        
        # Create demo tasks if there are none
        if Task.objects.count() == 0:
            priorities = ['low', 'medium', 'high']
            statuses = ['pending', 'in_progress', 'completed']
            
            # Create 10 sample tasks
            for i in range(1, 11):
                priority = random.choice(priorities)
                status = random.choice(statuses)
                deadline = timezone.now() + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None
                
                task = Task.objects.create(
                    title=f'Sample Task {i}',
                    description=f'This is a sample task description for task {i}.',
                    priority=priority,
                    status=status,
                    deadline=deadline,
                    assigned_to=regular_user if i % 2 == 0 else admin_user,
                    created_by=admin_user
                )
                
                # Add a sample comment to each task
                Comment.objects.create(
                    task=task,
                    user=admin_user if i % 2 == 0 else regular_user,
                    content=f'This is a sample comment on task {i}.'
                )
            
            self.stdout.write(self.style.SUCCESS('Sample tasks and comments created'))
        else:
            self.stdout.write(self.style.SUCCESS('Tasks already exist, skipping sample data creation'))
        
        self.stdout.write(self.style.SUCCESS('Todo App setup completed successfully!'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(self.style.SUCCESS('Admin: username=admin, password=adminpassword'))
        self.stdout.write(self.style.SUCCESS('User: username=user, password=userpassword')) 