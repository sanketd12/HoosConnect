from django.test import TestCase
from django.contrib.auth.models import User
from .models import Org, TaskFile, UserInOrg, Project, Task, UserAssignedToTask
from django.utils import timezone
from datetime import timedelta


class OrgModelTest(TestCase):
    def test_org_creation(self):
        org = Org.objects.create(org_name="TestOrg")
        self.assertEqual(org.org_name,"TestOrg")
        self.assertTrue(isinstance(org,Org))


# class TaskFileTest(TestCase):
#     def setUp(self):
#         self.org = Org.objects.create(org_name="Test Org")
#         self.user = User.objects.create_user(username="testuser", password="123")
        
#     def test_task_file_creation(self):
#         task_file = TaskFile.objects.create(
#             title="Test File",
#             file="file.txt",
#             org=self.org,
#             uploaded_by=self.user
#         )
#         self.assertEqual(task_file.title, "Test File")

    

class UserInOrgTest(TestCase):
    def setUp(self):
        self.org = Org.objects.create(org_name="Test Org")
        self.user = User.objects.create_user(username="testuser", password="123")
    
    def test_user_in_org(self):
        user_in_org = UserInOrg.objects.create(org_id=self.org, user_id=self.user)
        self.assertEqual(user_in_org.org_id, self.org)
        self.assertEqual(user_in_org.user_id, self.user)   


class TaskModelTest(TestCase):
    def setUp(self):
        self.org = Org.objects.create(org_name="Test Org")
        self.user = User.objects.create_user(username="testuser", password="123")
        self.project = Project.objects.create(
            org_id=self.org,
            user_id=self.user,
            project_name="Test Project",
            due_date=timezone.now() + timedelta(days=7),
            project_status="in progress"
        )  

    def test_task_creation(self):
        task = Task.objects.create(
            project_id=self.project,
            task_name = "Test Task",
            due_date=timezone.now() + timedelta(days=3),
            task_status="not started"
        )
        self.assertEqual(task.task_name, "Test Task")
        self.assertEqual(task.task_status, "not started")
        