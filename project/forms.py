from django import forms
from django.contrib.auth.models import User
from .models import Project, TaskFile, Task, Org, UserAssignedToTask, TaskMessage


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name']
        widgets = {
            'project_name': forms.TextInput(attrs={'placeholder': 'Project Name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].label = "Project Name"


class ProjectDeleteForm(forms.Form):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, user=None, org_id=None, is_pma_admin=False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_pma_admin:
            self.fields['projects'].queryset = Project.objects.filter(org_id=org_id)
        elif user:
            self.fields['projects'].queryset = Project.objects.filter(user_id=user.id, org_id=org_id)


class TaskFileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = ['title', 'file', 'file_description', 'keywords']

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        title = cleaned_data.get('title')

        if not file:
            raise forms.ValidationError("You must select a file to upload.")
        if not title:
            raise forms.ValidationError("File title is required.")
        return cleaned_data


class CreateTaskForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # add fields for file upload
    file_title = forms.CharField(max_length=255, required=False)
    file = forms.FileField(required=False)
    file_description = forms.CharField(widget=forms.Textarea, required=False)
    file_keywords = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Task
        fields = ['task_name', 'description', 'due_date', 'task_status', 'collaborators']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'task_status': forms.Select(choices=Task.STATUS_CHOICES),
        }
    
    def __init__(self, *args, org_id=None, user=None, project_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id  # store project_id to use in save
        self.user = user

        # fetch organization users and project creator
        project_creator = User.objects.filter(project__project_id=project_id).first()
        org_users = User.objects.filter(userinorg__org_id=org_id).exclude(id=project_creator.id)

        # set collaborators queryset
        self.fields['collaborators'].queryset = org_users.exclude(id=project_creator.id)
    
        if not org_users.exists():
            self.fields['collaborators'].help_text = "No one other than the project creator has joined the organization yet."

        # self.fields['collaborators'].queryset = User.objects.filter(userinorg__org_id=org_id)

    def clean(self):
        """custom validation logic"""
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        file_title = cleaned_data.get('file_title')

        # ensure file title is required IF a file is uploaded
        if file and not file_title:
            self.add_error('file_title', 'File title is required if a file is chosen.')

        return cleaned_data

    def save(self, commit=True):
        task = super().save(commit=False)
        # explicitly set the project_id
        if self.project_id:
            task.project_id_id = self.project_id   
        if commit:
            task.save()
            # add project/task creator as a collaborator
            creator = self.user
            UserAssignedToTask.objects.create(task_id=task, user_id=creator)
            # add any additional collaborators to the task
            for collaborator in self.cleaned_data['collaborators']:
                if collaborator != creator:
                    UserAssignedToTask.objects.create(task_id=task, user_id=collaborator)
            # save uploaded file if provided
            if self.cleaned_data.get('file'):
                TaskFile.objects.create(
                    task=task,
                    uploaded_by=self.user,
                    title=self.cleaned_data['file_title'],
                    file=self.cleaned_data['file'],
                    file_description=self.cleaned_data['file_description'],
                    keywords=self.cleaned_data['file_keywords'],
                )
        return task


class EditTaskForm(forms.ModelForm):
    collaborators = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = ['task_name', 'description', 'due_date', 'task_status', 'collaborators']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'task_status': forms.Select(choices=Task.STATUS_CHOICES),
        }

    # def __init__(self, *args, user=None, org_id=None, project_owner_id=None, instance=None, **kwargs):
    #     super().__init__(*args, instance=instance, **kwargs)
    #     self.user = user

    #     # exclude project owner from collaborators
    #     self.fields['collaborators'].queryset = User.objects.filter(userinorg__org_id=org_id).exclude(id=project_owner_id)

    #     # pre-select current collaborators
    #     if instance:
    #         self.fields['collaborators'].initial = instance.userassignedtotask_set.values_list('user_id', flat=True)

    def __init__(self, *args, user=None, org_id=None, project_owner_id=None, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        self.user = user

        # fetch organization users and exclude project owner
        org_users = User.objects.filter(userinorg__org_id=org_id).exclude(id=project_owner_id)

        self.fields['collaborators'].queryset = org_users

        # pre-select collaborators
        if instance:
            self.fields['collaborators'].initial = instance.userassignedtotask_set.values_list('user_id', flat=True)
        
        if not org_users.exists():
            self.fields['collaborators'].help_text = "No one other than the project creator has joined the organization yet."

    def save(self, commit=True):
        task = super().save(commit=False)
        if commit:
            task.save()

            # retrieve the project owner
            project_owner = task.project_id.user_id

            if 'collaborators' in self.cleaned_data:
                # delete previously assigned collaborators
                UserAssignedToTask.objects.filter(task_id=task).delete()
                # add project/task creator as a collaborator
                UserAssignedToTask.objects.create(task_id=task, user_id=project_owner)
                # add any new collaborators
                for collaborator in self.cleaned_data['collaborators']:
                    if collaborator != project_owner:  # avoid duplicating the project owner
                        UserAssignedToTask.objects.create(task_id=task, user_id=collaborator)
        return task


class TaskMessageForm(forms.ModelForm):
    class Meta:
        model = TaskMessage
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Type your message here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(TaskMessageForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = ''  # remove the label
