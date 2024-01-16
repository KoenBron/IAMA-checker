from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Assesment

# Create your tests here.
class BaseViewsTestCase(TestCase):
    fixtures = ["questions.json", "references.json"]
    
    def create_authorised_user(self):
        user = User.objects.create_user(username="Bob", password="password")
        self.client.login(username="Bob", password="password")
        return user

    def create_other_authorised_user(self):
        user = User.objects.create_user(username="Alice", password="password")
        self.client.login(username="Alice", password="password")
        return user
    
    def create_authorised_user_assesment(self):
        user = self.create_authorised_user()
        assesment = Assesment(name="testassesment", organisation="testorg", user=user)
        assesment.save()
        return assesment
            

class HomeViewTestCase(BaseViewsTestCase):

    def test_home_page_unauthorised(self):
        '''
        Test if you can access the home page if you are not authorised
        and return to the login screen.  
        '''
        response = self.client.get(reverse("base:home"))       
        self.assertTemplateUsed("login.html")
        self.assertEqual(response.status_code, 302)

    def test_home_page_authorised(self):
        '''
        Test if you can acces the home page with an authorised user
        '''
        self.create_authorised_user()
        self.assertTemplateUsed("base/home.html")


class DetailViewTestCase(BaseViewsTestCase):

    def test_detail_page_logged_in(self):
        '''
        Test whether the detail page of a newly created assesment is shown
        '''
        assesment = self.create_authorised_user_assesment()
        response = self.client.get(reverse("base:detail", args=(assesment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/detail.html")
        self.assertEqual(response.context["assesment"], assesment)

    def test_unauthorised_detail_page(self):
        '''
        Test wheter a logged in user can access the detail page of a different user's assesment
        '''
        assesment = self.create_authorised_user_assesment()
        User.objects.create_user(username="alice", password="password")
        self.client.login(username="alice", password="password")
        response = self.client.get(reverse("base:detail", args=(assesment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker heeft geen toegang tot deze assesment!")
    

class CreateAssesmentTestCase(BaseViewsTestCase):

    def test_create_assesment(self):
        '''
        Test wether an authorised user can create an assesment succesfully 
        '''
        self.create_authorised_user()
        response = self.client.post(reverse("base:create_assesment"), data={"name": "test_assesment", "organisation": "testorganisation"})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("base/detail.html")
        self.assertIsNotNone(Assesment.objects.get(name="test_assesment"))
        


class DeleteAssesmentTestCase(BaseViewsTestCase):

    def test_unauthorised_delete_assesment(self):
        '''
        Test wether a user can delete other users assesments
        '''
        assesment = self.create_authorised_user_assesment()
        User.objects.create_user(username="Alice", password="password")
        login = self.client.login(username="Alice", password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("base:delete_assesment", args=(assesment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker is niet toegestaan om deze assesment te verwijderen!")

    def test_delete_assesment(self):
        '''
        Test wether an authorised user can delete their assesment
        '''
        assesment = self.create_authorised_user_assesment()
        response = self.client.get(reverse("base:delete_assesment", args=(assesment.id,)))
        try:
            Assesment.objects.get(pk=assesment.id)
        except (KeyError, Assesment.DoesNotExist):
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed("base/home.html") 
        else:
            raise AssertionError("Assesment wasn't deleteted from the db.")


class UpdateAssesmentTestCase(BaseViewsTestCase):

    def test_update_assesment(self):
        '''
        Test wether an update of an assesment is executed correctly when used with expected behaviour
        '''
        assesment = self.create_authorised_user_assesment()
        response = self.client.post(reverse("base:update_assesment", args=(assesment.id,)), data={"name": "other_name", "organisation": "other_org"})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("base/detail.html")
        self.assertTrue(Assesment.objects.filter(name="other_name", organisation="other_org").exists())
        
    def test_update_assesment_unauthorised(self):
        '''
        Test wheter a user can update another users assesment
        '''
        assesment = self.create_authorised_user_assesment()
        self.create_other_authorised_user()
        response = self.client.post(reverse("base:update_assesment", args=(assesment.id,)), data={"name": "other_name", "organisation": "other_org"})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Assesment om te updaten bestaat niet!")
        self.assertFalse(Assesment.objects.filter(name="other_name", organisation="other_org").exists())







