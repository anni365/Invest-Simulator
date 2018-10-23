from django.test import TestCase
from .models import CustomUser, Transaction, UserAsset
from .forms import SignUpForm, UpdateProfileForm, BuyForm

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


class TransactionTest(TestCase):

    def setUp(self):
        Transaction.objects.create(user_id= 1, user_asset_id=2,
                  value_buy=2.3, value_sell=2.5, amount=3,
                  date="2018-10-08", type_transaction="compra")
        UserAsset.objects.create(user_id= 1, name="Dolar", total_amount=3,
                type_asset="Divisa", old_unit_value=2.3)

    def test_transaction_buy_user(self):
        transaction = Transaction.objects.get(user_id=1)
        self.assertEqual(transaction.value_buy, 2.3)

    def test_asset_user(self):
        asset = UserAsset.objects.get(user_id=1)
        self.assertEqual(asset.name, "Dolar")

    def test_transaction_asset_amount_user(self):
        transaction = Transaction.objects.get(user_id=1)
        asset = UserAsset.objects.get(user_id=1)
        self.assertEqual(transaction.amount, asset.total_amount)

    def test_valid_form_buy_valid(self):
        user_asset = UserAsset.objects.get(user_id=1)
        data = {'name':user_asset.name,
                'total_amount':user_asset.total_amount,}
        form = BuyForm(data=data)
        self.assertIs(form.is_valid(), False)
