import boto3
from botocore.exceptions import ClientError
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TaskFileForm, ProjectForm, ProjectDeleteForm, CreateTaskForm, EditTaskForm, TaskMessageForm
from .models import TaskFile, UserInOrg, Project, Task, Org, UserAssignedToTask, TaskMessage


class index(TemplateView):    
    template_name = 'project/index.html'


'''
create projects
'''
@login_required
def edit_project_view(request, org_id):
    org = get_object_or_404(Org, pk=org_id, userinorg__user_id=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        
        if form.is_valid():
            project_name = form.cleaned_data['project_name']

            # check if a project with the same name exists in the organization
            if Project.objects.filter(project_name=project_name, org_id=org).exists():
                messages.error(request, "A project with this name already exists in the selected organization.")
                return redirect('org_project_list', org_id=org_id)
            else:
                # create and save the project, setting user and organization
                project = form.save(commit=False)
                project.user_id = request.user
                project.org_id = org
                project.save()
                messages.success(request, f"You have successfully created the project: {project_name}.")
                return redirect('add_task', org_id=org_id, project_id=project.pk)
    else:
        form = ProjectForm()

    return render(request, 'project/edit_project.html', {
        'form': form,
        'org': org,
        'org_id': org_id,
    })


'''
delete projects
'''
@login_required
def delete_project_view(request, org_id):
    is_pma_admin = request.session.get('is_pma_admin', False)

    if is_pma_admin:
        # PMA Admins can bypass membership requirements
        org = get_object_or_404(Org, pk=org_id)
    else:
        # regular users must belong to the organization
        org = get_object_or_404(Org, pk=org_id, userinorg__user_id=request.user)

    if request.method == 'POST':
        delete_form = ProjectDeleteForm(request.POST, user=request.user, org_id=org_id, is_pma_admin=is_pma_admin)
        
        if delete_form.is_valid():
            projects_to_delete = delete_form.cleaned_data['projects']
            project_names = list(projects_to_delete.values_list('project_name', flat=True))
            projects_to_delete.delete()
            
            if len(project_names) == 1:
                messages.success(request, f"You have successfully deleted {project_names[0]}.")
            elif len(project_names) > 1:
                project_list_str = ", ".join(project_names)
                messages.success(request, f"You have successfully deleted {project_list_str}.")
            return redirect('org_project_list', org_id=org_id)
    else:
        delete_form = ProjectDeleteForm(user=request.user, org_id=org_id, is_pma_admin=is_pma_admin)

    return render(request, 'project/delete_project.html', {
        'delete_form': delete_form,
        'org': org,
        'org_id': org_id,
    })


'''
add task for a new project
'''
@login_required
def add_task_view(request, org_id, project_id):
    org = get_object_or_404(Org, pk=org_id, userinorg__user_id=request.user)
    project = get_object_or_404(Project, pk=project_id, org_id=org)

    # restrict task creation to project owner
    if project.user_id != request.user:
        return redirect('org_project_list', org_id=org_id)

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, request.FILES, org_id=org_id, user=request.user, project_id=project_id)
        if form.is_valid():
            form.save()
            return redirect('org_project_list', org_id=org_id)
    else:
        form = CreateTaskForm(org_id=org_id, user=request.user, project_id=project_id)

    return render(request, 'project/add_task.html', {
        'form': form,
        'org': org,
        'project': project,
    })


'''
edit task
'''
@login_required
def edit_task_view(request, org_id, task_id):
    task = get_object_or_404(Task, pk=task_id, project_id__org_id=org_id)
    org = get_object_or_404(Org, pk=org_id)

    is_pma_admin = request.session.get("is_pma_admin", False)
    is_assigned_user = UserAssignedToTask.objects.filter(task_id=task, user_id=request.user).exists()
    is_project_owner = task.project_id.user_id == request.user

    if not (is_pma_admin or is_assigned_user or is_project_owner):
        return redirect('org_project_list', org_id=org_id)

    project_owner_id = task.project_id.user_id.id
    task_files = TaskFile.objects.filter(task=task)

    # initialize forms
    form = EditTaskForm(
        request.POST if 'edit_task' in request.POST else None,
        user=request.user,
        instance=task,
        org_id=org_id,
        project_owner_id=project_owner_id
    )
    file_form = TaskFileForm(request.POST if 'upload_file' in request.POST else None, 
                             request.FILES if 'upload_file' in request.POST else None)

    if request.method == 'POST':
        if 'edit_task' in request.POST and form.is_valid():
            form.save()
            return redirect('org_project_list', org_id=org_id)

        elif 'upload_file' in request.POST and file_form.is_valid():
            task_file = file_form.save(commit=False)
            task_file.task = task
            task_file.uploaded_by = request.user
            task_file.save()
            messages.success(request, f"You have successfully uploaded: {task_file.title}")
            return redirect('org_project_list', org_id=org_id)

        elif 'delete_file' in request.POST:
            file_id = request.POST.get('delete_file')
            file_to_delete = get_object_or_404(TaskFile, id=file_id, task=task)
            if is_pma_admin or is_project_owner or file_to_delete.uploaded_by == request.user:
                file_title = file_to_delete.title
                file_to_delete.delete()
                messages.success(request, f"You have successfully deleted: {file_title}")
            return redirect('org_project_list', org_id=org_id)

    return render(request, 'project/edit_task.html', {
        'form': form,
        'file_form': file_form,
        'task': task,
        'task_files': task_files,
        'org': org,
        'is_pma_admin': is_pma_admin,
        'is_project_owner': is_project_owner,
    })


'''
delete task
'''
@login_required
def delete_task_confirm(request, org_id, task_id):
    # ensure the organization, project, and task exist
    org = get_object_or_404(Org, pk=org_id)
    task = get_object_or_404(Task, pk=task_id, project_id__org_id=org_id)

    is_pma_admin = request.session.get("is_pma_admin", False)
    is_project_owner = task.project_id.user_id == request.user

    # only allow PMA Admins or project owners to delete tasks
    if not (is_pma_admin or is_project_owner):
        return redirect('org_project_list', org_id=org_id)

    if request.method == 'POST':
        task.delete()
        return redirect('org_project_list', org_id=org_id)

    return render(request, 'project/confirm_delete_task.html', {
        'org_id': org_id,
        'task': task,
    })


@login_required
def serve_taskfile(request, org_id, file_id):
    taskfile = get_object_or_404(TaskFile, id=file_id)

    # org = get_object_or_404(Org, id=org_id)
    
    # set up the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    file_key = taskfile.file.name 

    try:
        # get the file URL (presigned URL for security or use public access)
        file_url = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': file_key},
                                             ExpiresIn=3600)  # URL expires in 1 hour
        
        # check the file type (file extension)
        file_extension = taskfile.file.name.split('.')[-1].lower()  # get the file extension
        
        # pass the file URL and file type to the template
        context = {
            'file_url': file_url,
            'taskfile': taskfile,
            'file_extension': file_extension,  # pass the file extension to the template
            'org_id': org_id,
        }

        return render(request, 'project/display_file.html', context)

    except ClientError as e:
        # if file is not found or another error occurs
        raise Http404(f"File not found: {str(e)}")


'''
displays each project (for a specific org) along with its task(s)
'''
@login_required
def org_project_list(request, org_id):
    # check if the user is in a PMA Admin session
    is_pma_admin = request.session.get("is_pma_admin", False)

    # retrieve org
    if is_pma_admin:
        # if PMA Admin, bypass membership requirement
        org = get_object_or_404(Org, org_id=org_id)
    else:
        # ensure the organization exists and the user is a member of it
        org = get_object_or_404(Org, org_id=org_id, userinorg__user_id=request.user)

    # retrieve all projects associated with the organization
    projects = Project.objects.filter(org_id=org)

    # collect tasks for each project along with their collaborators
    project_tasks = []
    for project in projects:
        tasks_with_collaborators = []
        tasks = Task.objects.filter(project_id=project).order_by('-created_at')

        is_project_owner = project.user_id == request.user
        
        for task in tasks:
            # collaborators = User.objects.filter(userassignedtotask__task_id=task)
            collaborators = User.objects.filter(
                userassignedtotask__task_id=task,
                userinorg__org_id=org_id  # filter by organization membership
            )
            files = TaskFile.objects.filter(task=task)
            is_task_collaborator = UserAssignedToTask.objects.filter(task_id=task, user_id=request.user).exists()

            # retrieve the top 3 most recent messages
            task_messages = TaskMessage.objects.filter(task=task).order_by('-msg_timestamp')[:3]

            # create a TaskMessageForm instance for each task
            message_form = TaskMessageForm()

            tasks_with_collaborators.append({
                'task': task,
                'collaborators': collaborators,
                'files': files,
                'is_task_collaborator': is_task_collaborator,
                'messages': task_messages,
                'message_form': message_form,
            })
        
        project_tasks.append({
            'project': project,
            'tasks': tasks_with_collaborators,
            'is_project_owner': is_project_owner,
        })

    # handle task message form submission (post message)
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, pk=task_id, project_id__org_id=org_id)

        form = TaskMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.user = request.user
            new_message.task = task
            new_message.save()
        else:
            messages.error(request, "Failed to post the message. Please try again.")

        return redirect('org_project_list', org_id=org_id)
    
    return render(request, 'project/org_project_list.html', {
        'org': org,
        'project_tasks': project_tasks,
        'org_id': org_id,
        'is_pma_admin': is_pma_admin,
    })


@login_required
def join_request_view(request, org_id, task_id):
    org = get_object_or_404(Org, pk=org_id)
    task = get_object_or_404(Task, pk=task_id)

    return render(request, 'project/join_request.html', {
        'org': org,
        'task': task,
    })


@login_required
def task_message_view(request, org_id, task_id):
    task = get_object_or_404(Task, pk=task_id, project_id__org_id=org_id)

    # Check session for PMA Admin
    is_pma_admin = request.session.get("is_pma_admin", False)
    is_assigned_user = task.userassignedtotask_set.filter(user_id=request.user).exists()
    is_project_owner = task.project_id.user_id == request.user

    if not (is_assigned_user or is_project_owner or is_pma_admin):
        return redirect('org_project_list', org_id=org_id)

    # Retrieve all messages for the task
    messages = TaskMessage.objects.filter(task=task).order_by('msg_timestamp')

    # Handle form submission
    if request.method == 'POST':
        form = TaskMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.user = request.user
            new_message.task = task
            new_message.save()
            return redirect('task_message', org_id=org_id, task_id=task_id)
    else:
        form = TaskMessageForm()

    # Pass `is_pma_admin` correctly
    return render(request, 'project/task_message.html', {
        'task': task,
        'messages': messages,
        'form': form,
        'org_id': org_id,
        'is_pma_admin': is_pma_admin,  # Correct key for template
    })


@login_required
def delete_task_message(request, org_id, task_id, message_id):
    task = get_object_or_404(Task, pk=task_id, project_id__org_id=org_id)
    message = get_object_or_404(TaskMessage, pk=message_id, task=task)

    is_pma_admin = request.session.get("is_pma_admin", False)
    is_message_owner = message.user == request.user
    is_project_owner = task.project_id.user_id == request.user

    if not (is_pma_admin or is_message_owner or is_project_owner):
        return redirect('task_message', org_id=org_id, task_id=task_id)

    message.delete()
    return redirect('task_message', org_id=org_id, task_id=task_id)


def public_org_project_list(request):
    # fetch all organizations and their associated projects
    organizations = Org.objects.all().prefetch_related('project_set')

    org_projects = []
    for org in organizations:
        projects = org.project_set.all()  # get all projects for this organization
        org_projects.append({
            'org_name': org.org_name,
            'projects': [project.project_name for project in projects],
        })

    return render(request, 'project/public_org_project_list.html', {'org_projects': org_projects})

