from django.test import TestCase, RequestFactory
from .models import CustomUser, Transaction, UserAsset, Alarm
from .views import cons_ranking

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
    Verificación del capital inicial del usuario logueado.
    """
    def test_initial_user_capital(self):
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
    def test_current_money_after_buy(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        CustomUser.update_money_user(request, 5, price, custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 875)

    """
    Verificación del dinero actual del usuario logueado después de hacer una
    venta de un activo.
    """
    def test_current_money_after_sell(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        CustomUser.update_money_user(request, 3, price, custom_user.virtual_money)
        self.assertEqual(custom_user.virtual_money, 1069)

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
    def test_add_one_sell_transaction_to_user(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        Transaction.addTransaction(request, price[0], price[1], 4, 1)
        user_transactions = Transaction.objects.filter(user=custom_user)
        user_assets = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(len(user_transactions), 1)
        self.assertEqual(user_transactions[0].type_transaction, "venta")

    """
    El usuario logueado quiere hacer una transacción de una compra de activos
    cuyo valor supera su dinero virtual.
    Se verifica que la transacción no se efectúa y dicho dinero sea el mismo.
    """
    def test_no_money_for_transaction(self):
        custom_user = CustomUser.objects.get(pk=1)
        current_money = custom_user.virtual_money
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        user_t_before = Transaction.objects.filter(user=custom_user)
        Transaction.addTransaction(request, price[0], price[1], 100, 1)
        user_t_after = Transaction.objects.filter(user=custom_user)
        self.assertEqual(len(user_t_before), len(user_t_after))
        self.assertEqual(custom_user.virtual_money, current_money)

    """
    El usuario logueado quiere vender una cantidad de activos que es superior
    a la que actualmente tiene.
    Se verifica que la cantidad actual de ese activo no cambia debido a que
    la transacción no se realiza.
    """
    def test_sell_more_assets_than_current_amount(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [23, 25]
        request = self.factory.get('/sell/')
        request.user = custom_user
        #Agrego activos al usuario.
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], False)
        user_assets_before = UserAsset.objects.filter(user=custom_user)
        current_a_before = user_assets_before[0].total_amount
        Transaction.addTransaction(request, price[0], price[1], 10, 1)
        user_assets_after = UserAsset.objects.filter(user=custom_user)
        current_a_after = user_assets_after[0].total_amount
        self.assertEqual(current_a_before, current_a_after)

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
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], False)
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
        UserAsset.addAsset(request, "Apple", 3, "Share", price[1], True)
        user_assets = UserAsset.objects.filter(user=custom_user)
        UserAsset.update_asset(user_assets[0], 7, price, True)
        self.assertEqual(user_assets[0].total_amount, 10)

    """
    Se verifica que no se pueda agregar un activo con un precio negativo.
    Se comparan las cantidades antes de intentar agregar ese activo y después.
    """
    def test_add_asset_to_user_with_negative_price(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        price = [-23, -25]
        request = self.factory.get('/buy/')
        request.user = custom_user
        UserAsset.addAsset(request, "Apple", 2, "Share", 25, False)
        user_a_before = UserAsset.objects.filter(user=custom_user)
        UserAsset.addAsset(request, "Apple", 5, "Share", price[1], False)
        user_a_after = UserAsset.objects.filter(user=custom_user)
        self.assertEqual(user_a_before[0].total_amount, user_a_after[0].total_amount)

    """
    Se comprueba que el único usuario registrado esté en primer lugar en el
    ranking.
    """
    def test_first_position_for_user_ranking(self):
        custom_user = CustomUser.objects.get(pk=1)
        self.assertTrue(custom_user.is_active)
        ranking = cons_ranking()
        self.assertEqual(ranking[0][0], 1)

    """
    Se comprueba que el usuario logueado está en el puesto 2 del ranking
    debido a que su capital es menor al del usuario recién registrado.
    """
    def test_second_position_for_user_ranking(self):
        CustomUser.objects.create(username="usuario2", email="usuario2@example.com",
            first_name="Nombre2", last_name="Apellido2", password="user2458")
        price = [23, 25]
        request = self.factory.get('/buy/')
        custom_user = CustomUser.objects.get(pk=2)
        request.user = custom_user
        #Agrego activos al usuario2, éste tendrá un capital mayor al usuario1.
        UserAsset.addAsset(request, "Apple", 5, "Share", price[1], False)
        ranking = cons_ranking()
        self.assertEqual(ranking[1][0], 2)

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
        Alarm.addAlarm(request, "Compra", "Superior", 25, 23, "Apple")
        user_alarms = Alarm.objects.filter(user=custom_user)
        self.assertEqual(len(user_alarms), 1)
