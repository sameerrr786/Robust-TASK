from django.contrib import admin
from .models import Task, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'priority', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'priority', 'assigned_to')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [CommentInline]

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'created_at')
    list_filter = ('user',)
    search_fields = ('content',)

admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
