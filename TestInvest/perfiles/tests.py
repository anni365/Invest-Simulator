from django.test import TestCase, RequestFactory
from .models import CustomUser, Transaction, UserAsset

class UserDataTest(TestCase):

    def setUp(self):
        self.credentials = {
            "username":"usuario1",
            "email":"usuario1@example.com",
            "first_name":"Nombre1",
            "last_name":"Apellido1",
            "password":"user2458"
        }
        CustomUser.objects.create_user(**self.credentials)
        self.factory = RequestFactory()

    """
    Se verifica que el usuario creado anteriormente pueda loguearse.
    """
    def test_login(self):
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)

    """
    Verificación del capital inicial del usuario creado y logueado.
    """
    def test_calculate_initial_capital_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        assets = UserAsset.objects.all()
        my_assets = UserAsset.objects.filter(user=custom_user)
        current_money = CustomUser.calculate_capital(assets, my_assets, custom_user.virtual_money)
        self.assertEqual(current_money, 1000)

    """
    Verificación del dinero actual del usuario logueado después de hacer una
    compra de un activo.
    """
    def test_calculate_current_money_after_buy(self):
        custom_user = CustomUser.objects.get(pk=1)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        CustomUser.update_money_user(request, 5, price, custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 885)

    """
    Verificación del dinero actual del usuario logueado después de hacer una
    venta de un activo.
    """
    def test_calculate_current_money_after_sell(self):
        custom_user = CustomUser.objects.get(pk=1)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        CustomUser.update_money_user(request, 3, price, custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 1075)

    """
    Se verifica que una nueva transacción pueda guardarse correctamente para
    el usuario logueado.
    """
    def test_first_user_transaction(self):
        custom_user = CustomUser.objects.get(pk=1)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
