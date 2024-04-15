from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Assesment, Question, Answer
from .base_view_helper import user_has_edit_privilidge
from .views import create_assesment

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

    def create_custom_authorised_user(self, name="Defaul_user"):
        user = User.objects.create_user(username=name, password="password")
        self.client.login(username="Alice", password="password")
        return user
    
    def create_assesment(self, user):
        assesment = Assesment(name="testassesment", organisation="testorg", user=user)
        assesment.save()
        return assesment

    def create_authorised_user_assesment(self):
        user = self.create_authorised_user()
        assesment = create_assesment(user)
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


class QuestionDetailTestCase(BaseViewsTestCase):

    def test_question_detail(self):
        '''
        Test wether question_detail shows itself properly with expected behaviour.
        For both a phase and questin page.
        '''
        assesment = self.create_authorised_user_assesment()
        response = self.client.get(reverse("base:question_detail", args=(assesment.id, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/phase_intro.html")
        question = Question.objects.get(id=1)
        self.assertEqual(response.context["question"], question)
        self.assertIsNotNone(response.context["reference_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["status_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["question_list"])
        self.assertIsNotNone(response.context["jobs"])

        # The same but for question instead of phase_intro  
        response = self.client.get(reverse("base:question_detail", args=(assesment.id, 2)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/q_detail.html")
        question = Question.objects.get(id=2)
        answer = Answer.objects.get(user=response.wsgi_request.user, question_id=question.id, assesment_id=assesment.id)
        self.assertEqual(response.context["question"], question)
        self.assertEqual(response.context["answer"], answer)
        self.assertIsNotNone(response.context["reference_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["status_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["question_list"])
        self.assertIsNotNone(response.context["collab_list"])
        self.assertIsNotNone(response.context["jobs"])

    def test_question_detail_unauthorised(self):
        '''
        Test wether an unauthorised user is blocked from accessing
        this page
        '''
        assesment = self.create_authorised_user_assesment()
        self.create_other_authorised_user()
        response = self.client.get(reverse("base:question_detail", args=(assesment.id, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker heeft geen toegang tot deze assesment!")


class EditPrivilidgeTestCase(BaseViewsTestCase):
    
    def test_with_author(self):
        '''
        Test wether function user_has_edit_priviliged() works as intended
        By testing if the user that created the assesment gets edit privilidges
        '''
        user = self.create_authorised_user()
        assesment = self.create_assesment(user)
        self.assertTrue(user_has_edit_privilidge(user.id, assesment))
        
    def test_with_user_in_user_group(self):
        '''
        Test wether the function works as excpected with a user that is in the user group of the asssesment 
        '''
        user = self.create_authorised_user()
        assesment = self.create_assesment(user)
        user2 = self.create_other_authorised_user()
        assesment.user_group.add(user2)
        self.assertTrue(user_has_edit_privilidge(user2.id, assesment))

    def test_with_unauthorised_user(self):
        '''
        Test wether the function works as excpected when the user isn't the author or part of the assesments user_group
        '''
        user = self.create_authorised_user()
        assesment = self.create_assesment(user)
        user2 = self.create_other_authorised_user()
        self.assertFalse(user_has_edit_privilidge(user2.id, assesment))


class EditorAPITestCase(BaseViewsTestCase):

    def test_adding_editor(self):
        '''
        Test wether the api succesfully adds an editor to an assesments usergroup when added by authorised user
        '''
        editor = self.create_other_authorised_user()
        user = self.create_authorised_user()
        assesment = self.create_assesment(user)
        response = self.client.get(reverse("base:add_editor", args=(assesment.id, editor.id,)))
        self.assertTemplateUsed("base/detail.html")
        self.assertEqual(response.status_code, 302)
        self.assertIn(editor, assesment.user_group.all())

    def test_adding_editor_with_unauthorised_user(self):
        '''
        Test whether the api denies adding an editor when it's done by an unauthorised user
        '''
        user = self.create_authorised_user()
        assesment = self.create_assesment(user)
        unauthorised_user = self.create_other_authorised_user() # Login as another user that has no editing privilidges
        response = self.client.get(reverse("base:add_editor", args=(assesment.id, unauthorised_user.id,)))
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Alleen de maker van een assesment kan editors toevoegen!")








