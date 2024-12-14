# Generated by Django 5.1.2 on 2024-10-21 14:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Org",
            fields=[
                ("org_id", models.AutoField(primary_key=True, serialize=False)),
                ("org_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("project_id", models.AutoField(primary_key=True, serialize=False)),
                ("project_name", models.CharField(max_length=100)),
                ("due_date", models.DateField()),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "project_status",
                    models.CharField(
                        choices=[
                            ("not started", "Not Started"),
                            ("in progress", "In Progress"),
                            ("completed", "Completed"),
                            ("stuck", "Stuck"),
                            ("awaiting review", "Awaiting Review"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "org_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="project.org"
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("project_id", "org_id")},
            },
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                ("task_id", models.AutoField(primary_key=True, serialize=False)),
                ("task_name", models.CharField(max_length=100)),
                ("due_date", models.DateField()),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "task_status",
                    models.CharField(
                        choices=[
                            ("not started", "Not Started"),
                            ("in progress", "In Progress"),
                            ("completed", "Completed"),
                            ("stuck", "Stuck"),
                            ("awaiting review", "Awaiting Review"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "project_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.project",
                    ),
                ),
            ],
            options={
                "unique_together": {("task_id", "project_id")},
            },
        ),
        migrations.CreateModel(
            name="TaskFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("file", models.FileField(upload_to="media/")),
                (
                    "file_type",
                    models.CharField(
                        choices=[
                            ("txt", "Text File"),
                            ("pdf", "PDF Document"),
                            ("jpg", "Image"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="project.org",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserAssignedToTask",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "task_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="project.task"
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user_id", "task_id")},
            },
        ),
        migrations.CreateModel(
            name="UserInOrg",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "org_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="project.org"
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("org_id", "user_id")},
            },
        ),
    ]
