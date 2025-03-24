from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Assessment, Question, Answer
from .base_view_helper import user_has_edit_privilidge
from .views import create_assessment

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
    
    def create_assessment(self, user):
        assessment = Assessment(name="testassessment", organisation="testorg", user=user)
        assessment.save()
        return assessment

    def create_authorised_user_assessment(self):
        user = self.create_authorised_user()
        assessment = create_assessment(user)
        return assessment
            

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
        Test whether the detail page of a newly created assessment is shown
        '''
        assessment = self.create_authorised_user_assessment()
        response = self.client.get(reverse("base:detail", args=(assessment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/detail.html")
        self.assertEqual(response.context["assessment"], assessment)

    def test_unauthorised_detail_page(self):
        '''
        Test wheter a logged in user can access the detail page of a different user's assessment
        '''
        assessment = self.create_authorised_user_assessment()
        User.objects.create_user(username="alice", password="password")
        self.client.login(username="alice", password="password")
        response = self.client.get(reverse("base:detail", args=(assessment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker heeft geen toegang tot deze assessment!")
    

class CreateAssessmentTestCase(BaseViewsTestCase):

    def test_create_assessment(self):
        '''
        Test wether an authorised user can create an assessment succesfully 
        '''
        self.create_authorised_user()
        response = self.client.post(reverse("base:create_assessment"), data={"name": "test_assessment", "organisation": "testorganisation"})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("base/detail.html")
        self.assertIsNotNone(Assessment.objects.get(name="test_assessment"))
        


class DeleteAssessmentTestCase(BaseViewsTestCase):

    def test_unauthorised_delete_assessment(self):
        '''
        Test wether a user can delete other users assessments
        '''
        assessment = self.create_authorised_user_assessment()
        User.objects.create_user(username="Alice", password="password")
        login = self.client.login(username="Alice", password="password")
        self.assertTrue(login)
        response = self.client.get(reverse("base:delete_assessment", args=(assessment.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker is niet toegestaan om deze assessment te verwijderen!")

    def test_delete_assessment(self):
        '''
        Test wether an authorised user can delete their assessment
        '''
        assessment = self.create_authorised_user_assessment()
        response = self.client.get(reverse("base:delete_assessment", args=(assessment.id,)))
        try:
            Assessment.objects.get(pk=assessment.id)
        except (KeyError, Assessment.DoesNotExist):
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed("base/home.html") 
        else:
            raise AssertionError("Assessment wasn't deleteted from the db.")


class UpdateAssessmentTestCase(BaseViewsTestCase):

    def test_update_assessment(self):
        '''
        Test wether an update of an assessment is executed correctly when used with expected behaviour
        '''
        assessment = self.create_authorised_user_assessment()
        response = self.client.post(reverse("base:update_assessment", args=(assessment.id,)), data={"name": "other_name", "organisation": "other_org"})
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("base/detail.html")
        self.assertTrue(Assessment.objects.filter(name="other_name", organisation="other_org").exists())
        
    def test_update_assessment_unauthorised(self):
        '''
        Test wheter a user can update another users assessment
        '''
        assessment = self.create_authorised_user_assessment()
        self.create_other_authorised_user()
        response = self.client.post(reverse("base:update_assessment", args=(assessment.id,)), data={"name": "other_name", "organisation": "other_org"})
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Assessment om te updaten bestaat niet!")
        self.assertFalse(Assessment.objects.filter(name="other_name", organisation="other_org").exists())


class QuestionDetailTestCase(BaseViewsTestCase):

    def test_question_detail(self):
        '''
        Test wether question_detail shows itself properly with expected behaviour.
        For both a phase and questin page.
        '''
        assessment = self.create_authorised_user_assessment()
        response = self.client.get(reverse("base:question_detail", args=(assessment.id, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/phase_intro.html")
        question = Question.objects.get(id=1)
        self.assertEqual(response.context["question"], question)
        self.assertIsNotNone(response.context["reference_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["status_list"])
        self.assertIsNotNone(response.context["index_context_objects"]["question_list"])
        self.assertIsNotNone(response.context["jobs"])

        # The same but for question instead of phase_intro  
        response = self.client.get(reverse("base:question_detail", args=(assessment.id, 2)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("base/q_detail.html")
        question = Question.objects.get(id=2)
        answer = Answer.objects.get(user=response.wsgi_request.user, question_id=question.id, assessment_id=assessment.id)
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
        assessment = self.create_authorised_user_assessment()
        self.create_other_authorised_user()
        response = self.client.get(reverse("base:question_detail", args=(assessment.id, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Gebruiker heeft geen toegang tot deze assessment!")


class EditPrivilidgeTestCase(BaseViewsTestCase):
    
    def test_with_author(self):
        '''
        Test wether function user_has_edit_priviliged() works as intended
        By testing if the user that created the assessment gets edit privilidges
        '''
        user = self.create_authorised_user()
        assessment = self.create_assessment(user)
        self.assertTrue(user_has_edit_privilidge(user.id, assessment))
        
    def test_with_user_in_user_group(self):
        '''
        Test wether the function works as excpected with a user that is in the user group of the asssesment 
        '''
        user = self.create_authorised_user()
        assessment = self.create_assessment(user)
        user2 = self.create_other_authorised_user()
        assessment.user_group.add(user2)
        self.assertTrue(user_has_edit_privilidge(user2.id, assessment))

    def test_with_unauthorised_user(self):
        '''
        Test wether the function works as excpected when the user isn't the author or part of the assessments user_group
        '''
        user = self.create_authorised_user()
        assessment = self.create_assessment(user)
        user2 = self.create_other_authorised_user()
        self.assertFalse(user_has_edit_privilidge(user2.id, assessment))


class EditorAPITestCase(BaseViewsTestCase):

    def test_adding_editor(self):
        '''
        Test wether the api succesfully adds an editor to an assessments usergroup when added by authorised user
        '''
        editor = self.create_other_authorised_user()
        user = self.create_authorised_user()
        assessment = self.create_assessment(user)
        response = self.client.get(reverse("base:add_editor", args=(assessment.id, editor.id,)))
        self.assertTemplateUsed("base/detail.html")
        self.assertEqual(response.status_code, 302)
        self.assertIn(editor, assessment.user_group.all())

    def test_adding_editor_with_unauthorised_user(self):
        '''
        Test whether the api denies adding an editor when it's done by an unauthorised user
        '''
        user = self.create_authorised_user()
        assessment = self.create_assessment(user)
        unauthorised_user = self.create_other_authorised_user() # Login as another user that has no editing privilidges
        response = self.client.get(reverse("base:add_editor", args=(assessment.id, unauthorised_user.id,)))
        self.assertTemplateUsed("errors/error.html")
        self.assertEqual(response.context["message"], "Alleen de maker van een assessment kan editors toevoegen!")








