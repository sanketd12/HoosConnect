from django.db import models
from django.contrib.auth.models import User


class Org(models.Model):
    org_id = models.AutoField(primary_key=True) # auto-incrementing primary key
    org_name = models.CharField(max_length=100)

    def __str__(self):
        return self.org_name


class UserInOrg(models.Model):
    org_id = models.ForeignKey(Org, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('org_id', 'user_id')  # composite primary key
    
    def __str__(self):
        return f'User {self.user_id} in {self.org_id}'
    

class Project(models.Model):
    STATUS_CHOICES = [
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('stuck', 'Stuck'),
        ('awaiting review', 'Awaiting Review'),
    ]
    project_id = models.AutoField(primary_key=True)
    org_id = models.ForeignKey(Org, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=60)
    due_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    project_status = models.CharField(choices=STATUS_CHOICES, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project_id', 'org_id')  # composite primary key

    def __str__(self):
        return self.project_name
    

class Task(models.Model):
    STATUS_CHOICES = [
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('stuck', 'Stuck'),
        ('awaiting review', 'Awaiting Review'),
    ]
    task_id = models.AutoField(primary_key=True)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=60)
    due_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    task_status = models.CharField(choices=STATUS_CHOICES, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('task_id', 'project_id')  # composite primary key

    def __str__(self):
        return self.task_name
    

# add FileField for file upload
class TaskFile(models.Model):
    FILE_TYPES = [
        ('txt', 'Text File'),
        ('pdf', 'PDF Document'),
        ('jpg', 'Image'),
    ]
    
    title = models.CharField(max_length=60)
    file = models.FileField(upload_to='media/')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)  # associate file with task
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # associate file with user
    file_description = models.TextField(blank=True, null=True)  # description of file contents
    keywords = models.CharField(max_length=255, blank=True, null=True)  # keywords for identifying the file
    timestamp = models.DateTimeField(auto_now_add=True)  # timestamp when file is uploaded

    def __str__(self):
        return self.title
    

class UserAssignedToTask(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_id', 'task_id')
    
    def __str__(self):
        return f'User {self.user_id} assigned to Task {self.task_id}'
    

class TaskMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    msg_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content}'
