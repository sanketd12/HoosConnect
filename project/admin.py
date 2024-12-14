from django.contrib import admin
from .models import Org, UserInOrg, Project, Task, UserAssignedToTask, TaskFile

# Register all the models
admin.site.register(Org)
admin.site.register(UserInOrg)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(UserAssignedToTask)
admin.site.register(TaskFile)