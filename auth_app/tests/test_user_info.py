from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from auth_app.models import Profile
from unittest import skip

@skip("Disabling user_profile tests in CI, as `user_profile` page was removed in commit 3415b49")
class UserInfoViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(username= 'testuser', password= 'testpassword')
        self.client.login(username='testuser',password='testpassword')
        self.url = reverse('user_profile')

    def test_user_info_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code,200)
        
    def test_user_info_view_post_valid_data(self):
        data = {
            'computing_id': '123456',
            'preferred_name': 'Test User',
            'pronoun': 'she/her'
        }
        response = self.client.post(self.url,data)
        self.assertRedirects(response,'/user/')
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.computing_id,'123456')
        self.assertEqual(profile.preferred_name, 'Test User')
        self.assertEqual(profile.pronoun, 'she/her')

    def test_user_info_view_post_invalid_data(self):
        data = {
            'computing_id': '',
            'preferred_name': 'Test User',
            'pronoun': 'she/her'
        }
        response = self.client.post(self.url,data)
        self.assertEqual(response.status_code,302)
        ##self.assertFormError(response,'form','computing_id','This field is required')
