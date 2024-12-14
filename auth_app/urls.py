from django.urls import path
from . import views

urlpatterns = [
    # /user/
    path('', views.index, name='user'),
    # /user/profile
    path('profile/', views.profile_view, name='profile'),
    
    path('switch-role/', views.switch_role, name='switch_role'),

    path('manage_organizations/', views.manage_organizations, name='manage_organizations'),

    # path('org/<int:org_id>/delete/', views.confirm_delete_org, name='confirm_delete_org'),
]