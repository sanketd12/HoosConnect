from django import forms
from django.contrib.auth.models import User
from project.models import Org, UserInOrg
from auth_app.models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['computing_id', 'pronoun']


# class AddOrgForm(forms.ModelForm):
#     class Meta:
#         model = Org
#         fields = ['org_name']


class JoinOrgForm(forms.Form):
    join_organization = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={'class': 'searchable-dropdown'}),
        label=''
    )

    def __init__(self, *args, **kwargs):
        available_orgs = kwargs.pop('available_orgs', None)
        super().__init__(*args, **kwargs)

        if available_orgs:
            # sort organizations alphabetically by name
            sorted_orgs = sorted(available_orgs, key=lambda org: org.org_name)
            
            # add a placeholder option
            choices = [("", "--------")]  # default empty choice
            choices += [(org.org_id, org.org_name) for org in sorted_orgs]
            
            self.fields['join_organization'].choices = choices


class RemoveOrgForm(forms.Form):
    remove_organization = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='',
    )

    def __init__(self, *args, **kwargs):
        user_orgs = kwargs.pop('user_orgs')
        super().__init__(*args, **kwargs)

        if user_orgs.model == Org:  # PMA Admin: 'user_orgs' is a QuerySet of Org objects
            self.fields['remove_organization'].choices = [
                (org.org_name, org.org_name) for org in user_orgs
            ]
        else:  # regular User: 'user_orgs' is a QuerySet of UserInOrg objects
            self.fields['remove_organization'].choices = [
                (user_in_org.org_id.org_name, user_in_org.org_id.org_name) for user_in_org in user_orgs
            ]
