import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

class Cliente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cliente')
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r'^\+?[0-9 ()-]{7,20}$', 'Ingrese un teléfono válido.')])
    contactos = models.ManyToManyField('self', symmetrical=False, blank=True)
    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cuentas')
    numero = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    alias = models.CharField(max_length=60)
    saldo = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    creada = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.CheckConstraint(check=models.Q(saldo__gte=0), name='saldo_no_negativo')]
        ordering = ['id']
    def __str__(self):
        return f'{self.alias} · {self.cliente.nombre}'

class Transaccion(models.Model):
    TIPOS = [('deposito', 'Depósito'), ('retiro', 'Retiro'), ('transferencia', 'Transferencia')]
    referencia = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='movimientos')
    destino = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='recibidos', null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPOS)
    monto = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    descripcion = models.CharField(max_length=160, blank=True)
    creada = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = 'transacción'
        verbose_name_plural = 'transacciones'
        ordering = ['-creada', '-id']
        constraints = [models.CheckConstraint(check=models.Q(monto__gt=0), name='monto_positivo'),
            models.CheckConstraint(check=(models.Q(tipo='transferencia', destino__isnull=False) & ~models.Q(cuenta=models.F('destino'))) |
                models.Q(tipo__in=['deposito', 'retiro'], destino__isnull=True), name='destino_coherente')]
    def __str__(self):
        return f'{self.get_tipo_display()} ${self.monto}'
