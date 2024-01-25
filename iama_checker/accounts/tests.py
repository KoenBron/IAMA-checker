from django.test import TestCase
# from base.models import Assesment, Answer
from .forms import RegisterForm
from django.urls import reverse
from django.contrib.auth.models import User

# Create your tests here.
class RegisterTestCase(TestCase):

    def test_register_form_non_matching_passwords(self):
        '''
        Test whether the form doesn't accept mismatching passwords
        '''
        form = RegisterForm(data={"username": "testuser", "password1": "123", "password2": "234"})
        self.assertFalse(form.is_valid())

    def test_valid_user_creation(self):
        '''
        Test if register method with valid data creates a user
        '''
        response = self.client.post(reverse("accounts:register"), data={"username": "testuser", "password1": "password", "password2": "password"})
        user = User.objects.get(username="testuser")
        # Check for 302 as upon succes the user is logged in and redirected to the home page
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("base/home.html")
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)
