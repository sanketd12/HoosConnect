from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from project.models import Org, UserInOrg
from auth_app.models import Profile
from .forms import ProfileForm, JoinOrgForm, RemoveOrgForm, UserForm
from django.urls import reverse
from django.contrib import messages


@login_required
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    can_be_pma_admin = request.user.groups.filter(name="PMA Admin").exists()
    is_pma_admin = request.session.get('is_pma_admin', False)

    if request.session.get('is_pma_admin', False):
        # PMA Admins see all organizations
        user_orgs = Org.objects.all()
        org_details = [{'org_name': org.org_name, 'org_id': org.org_id} for org in user_orgs]
    else:
        # common users see their associated organizations
        user_orgs = UserInOrg.objects.filter(user_id=request.user).select_related('org_id')
        org_details = [{'org_name': user_org.org_id.org_name, 'org_id': user_org.org_id.org_id} for user_org in user_orgs]

    first_name = request.user.first_name if request.user.first_name else request.user.username
    last_name = request.user.last_name if request.user.last_name else ""

    context = {
        'user': request.user,
        'user_info': user_profile,
        'org_details': org_details,
        'computing_id': user_profile.computing_id if user_profile.computing_id else "NULL",
        'pronoun': user_profile.pronoun if user_profile.pronoun else None,
        'first_name': first_name,
        'last_name': last_name,
        'is_pma_admin': is_pma_admin,
        'can_be_pma_admin': can_be_pma_admin,
        'current_role': "PMA Admin" if request.session.get('is_pma_admin') else "Common User",
    }

    return render(request, 'auth_app/index.html', context)


@login_required
def switch_role(request):
    if not request.user.groups.filter(name="PMA Admin").exists():
        return redirect(reverse('user'))

    # toggle the session role
    if request.session.get('is_pma_admin'):
        request.session['is_pma_admin'] = False
    else:
        request.session['is_pma_admin'] = True

    return redirect(reverse('user'))


@login_required
def profile_view(request):
    user = request.user
    # get the associated profile
    profile = Profile.objects.get(user=user)

    # initialize forms for profile update
    user_form = UserForm(instance=user)
    profile_form = ProfileForm(instance=profile)

    # process POST request for updating profile
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/user/')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'auth_app/profile.html', context)


@login_required
def manage_organizations(request):
    is_pma_admin = request.session.get('is_pma_admin', False)

    user_orgs = UserInOrg.objects.filter(user_id=request.user).select_related('org_id')

    # organizations the user is not already a member of
    available_orgs = Org.objects.exclude(
        org_id__in=[user_in_org.org_id_id for user_in_org in user_orgs]
    )

    join_org_form = JoinOrgForm(available_orgs=available_orgs)
    remove_org_form = RemoveOrgForm(user_orgs=user_orgs)

    if request.method == 'POST':
        # joining an organization
        if 'join_org' in request.POST:
            join_org_form = JoinOrgForm(request.POST, available_orgs=available_orgs)
            if join_org_form.is_valid():
                org_id = join_org_form.cleaned_data['join_organization']
                org = Org.objects.get(pk=org_id)
                UserInOrg.objects.create(user_id=request.user, org_id=org)
                messages.success(request, f"You have successfully joined {org.org_name}.")
                return redirect('user')

        # removing organizations
        elif 'remove_org' in request.POST:
            remove_org_form = RemoveOrgForm(data=request.POST, user_orgs=user_orgs)
            if remove_org_form.is_valid():
                organizations_to_remove = remove_org_form.cleaned_data['remove_organization']
                removed_orgs = []
                for org_name in organizations_to_remove:
                    org = Org.objects.get(org_name=org_name)
                    UserInOrg.objects.filter(user_id=request.user, org_id=org).delete()
                    removed_orgs.append(org_name)
                
                if len(removed_orgs) == 1:
                    messages.success(request, f"You have successfully removed yourself from {removed_orgs[0]}.")
                elif len(removed_orgs) > 1:
                    messages.success(request, f"You have successfully removed yourself from {', '.join(removed_orgs)}.")
                
                return redirect('user')
            
    # pass information about whether the user is in any organization
    user_in_orgs = user_orgs.exists()

    context = {
        # 'add_org_form': add_org_form,
        'join_org_form': join_org_form,
        'remove_org_form': remove_org_form,
        'is_pma_admin': is_pma_admin,
        'user_in_orgs': user_in_orgs,
    }
    return render(request, 'auth_app/manage_organizations.html', context)

