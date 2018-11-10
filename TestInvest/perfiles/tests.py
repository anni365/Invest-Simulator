from django.test import TestCase, RequestFactory
from .models import CustomUser, Transaction, UserAsset, Alarm

class CustomUserTest(TestCase):

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
    Se verifica que un usuario no registrado no pueda iniciar sesión.
    """
    def test_login_false(self):
        data = {
            "username":"usuario2",
            "password":"user2458"
        }
        response = self.client.post('/login/', data, follow=True)
        self.assertFalse(response.context['user'].is_active)

    """
    Verificación del capital inicial del usuario creado y logueado.
    """
    def test_calculate_initial_capital_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
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
        self.assertTrue(custom_user.is_active)
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
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        CustomUser.update_money_user(request, 3, price, custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 1075)

class TransactionTest(TestCase):

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
        self.client.post('/login/', self.credentials, follow=True)

    """
    Se verifica que una nueva transacción de compra pueda guardarse
    correctamente para el usuario logueado.
    """
    def test_add_one_buy_transaction_to_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
        self.assertEqual(user_transactions[0].type_transaction, "compra")

    """
    Se verifica que una nueva transacción de venta pueda guardarse
    correctamente para el usuario logueado.
    """
    def test_add_one_buy_transaction_to_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
        self.assertEqual(user_transactions[0].type_transaction, "venta")

class UserAssetTest(TestCase):

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
        self.client.post('/login/', self.credentials, follow=True)

    """
    Se verifica que se pueda hacer agregar un activo al usuario logueado.
    """
    def test_add_asset_to_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1])
        user_assets = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(len(user_assets), 1)

    """
    Verificación de poder actualizar la cantidad actual de activos para el
    usuario logueado.
    """
    def test_update_user_asset_amount(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1])
        user_assets = UserAsset.objects.filter(user=custom_user)
        UserAsset.update_asset(user_assets[0], 7, price)
        self.assertEqual(user_assets[0].total_amount, 10)

class AlarmTest(TestCase):

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
        self.client.post('/login/', self.credentials, follow=True)

    """
    Verifica que se puede agregar correctamente una alarma para el usuario
    logueado.
    """
    def test_add_alarm_to_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        request = self.factory.get('/alarm/')
        request.user = custom_user
        Alarm.addAlarm(request, "Alta", "Compra", "Superior", 25, 23, "Apple")
        user_alarms = Alarm.objects.filter(user=custom_user)
        self.assertEqual(len(user_alarms), 1)
