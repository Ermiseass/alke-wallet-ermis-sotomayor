import getpass
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from gestion.models import Cliente, Cuenta
from gestion.services import operar
class Command(BaseCommand):
    help = 'Crea datos ficticios locales; solicita una contraseña y no la guarda en archivos.'
    def add_arguments(self, parser):
        parser.add_argument('--password', help='Solo para pruebas locales automatizadas.')
    @transaction.atomic
    def handle(self, *args, **options):
        if User.objects.filter(username='ermis').exists():
            self.stdout.write('El usuario ermis ya existe; no se modificó.')
            return
        password = options['password'] or getpass.getpass('Elige contraseña para ermis: ')
        validate_password(password)
        u = User.objects.create_user('ermis', password=password, is_staff=True, is_superuser=True)
        c = Cliente.objects.create(usuario=u, nombre='Ermis Sotomayor', email='ermis@example.com')
        other = User.objects.create_user('cliente_demo')
        d = Cliente.objects.create(usuario=other, nombre='Cliente de ejemplo', email='cliente@example.com')
        c.contactos.add(d)
        a = Cuenta.objects.create(cliente=c, alias='Cuenta principal')
        b = Cuenta.objects.create(cliente=c, alias='Mis ahorros')
        Cuenta.objects.create(cliente=d, alias='Cuenta de ejemplo')
        operar(usuario=u, cuenta_id=a.pk, tipo='deposito', monto='250000', descripcion='Carga inicial de demostración')
        operar(usuario=u, cuenta_id=a.pk, tipo='transferencia', destino_id=b.pk, monto='60000', descripcion='Ahorro del mes')
        operar(usuario=u, cuenta_id=a.pk, tipo='retiro', monto='15000', descripcion='Gastos de ejemplo')
        self.stdout.write(self.style.SUCCESS('Demo creada. Usuario: ermis. Saldo total: $235.000.'))
