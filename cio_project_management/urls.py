from django.contrib import admin
from django.urls import path,include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    # /home/
    path('home/', include('home.urls')),
    # /user/
    path('user/',include('auth_app.urls')),
    # allauth URLs for Google OAuth
    path('accounts/', include('allauth.urls')),
    # /project/
    path('project/', include('project.urls')),
    # is this doing anything?
    path('logout/', LogoutView.as_view(), name='logout'),

    path('', include('home.urls')),
]
