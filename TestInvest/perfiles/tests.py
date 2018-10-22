from django.test import TestCase
from .models import CustomUser
from .forms import SignUpForm, UpdateProfileForm

class CustomUserTest(TestCase):

    def setUp(self):
        CustomUser.objects.create(username="Camicba", email="camicba@example.com",
            first_name="Camila",last_name="Cuñer", password="pass2458")

    def test_custom_user_username(self):
        custom_user = CustomUser.objects.get(username="Camicba")
        self.assertEqual(custom_user.username, "Camicba")

    def test_custom_user_email(self):
        custom_user = CustomUser.objects.get(username="Camicba")
        self.assertTrue(custom_user.email != "camicba1@example.com")

    def test_valid_form_register(self):
        custom_user = CustomUser.objects.get(username="Camicba")
        data = {'username':custom_user.username,
                'email':custom_user.email,
                'email2':custom_user.email,
                'first_name':custom_user.first_name,
                'last_name':custom_user.last_name,
                'password1':custom_user.password,
                'password2':custom_user.password,}
        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())

    def test_valid_form_edit_profile(self):
        custom_user = CustomUser.objects.get(username="Camicba")
        data = {'email':'test@example.com',
                'first_name':custom_user.first_name,
                'last_name':custom_user.last_name,}
        form = UpdateProfileForm(data=data)
        self.assertTrue(form.is_valid())
