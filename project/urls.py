from django.urls import path
from . import views

urlpatterns = [
    # path("", views.get_user_projects, name="project"),

    # /project/<org_id>
    path('<int:org_id>/', views.org_project_list, name='org_project_list'),

    # /project/<org_id>/edit/
    path('<int:org_id>/edit/', views.edit_project_view, name='edit_project'),

    # /project/<org_id>/<project_id>/add_task/
    path('<int:org_id>/<project_id>/add_task/', views.add_task_view, name='add_task'),

    # /project/<org_id>/delete_project/
    path('<int:org_id>/delete_project/', views.delete_project_view, name='delete_project'),

    # /project/<org_id>/<task_id>/edit_task
    path('<int:org_id>/<int:task_id>/edit_task/', views.edit_task_view, name='edit_task'),

    # /project/<org_id>/<task_id>/message
    path('<int:org_id>/<int:task_id>/message/', views.task_message_view, name='task_message'),

    # /project/<org_id>/task/<task_id>/message/<message_id>/delete
    path('<int:org_id>/task/<int:task_id>/message/<int:message_id>/delete/', views.delete_task_message, name='delete_task_message'),

    # /project/join_request
    path('<int:org_id>/<int:task_id>/join_request/', views.join_request_view, name='join_request'),

    # /project/media/<org_id>/<file_id>
    path('media/<int:org_id>/<int:file_id>/', views.serve_taskfile, name='serve_taskfile'),

    # /project/public_projects
    path('public_projects/', views.public_org_project_list, name="public_org_project_list"),

    # /project/<org_id>/task/<task_id>/delete
    path('<int:org_id>/task/<int:task_id>/delete/', views.delete_task_confirm, name="delete_task_confirm"),
]