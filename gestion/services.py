"""Todas las operaciones monetarias pasan por este servicio atómico."""
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from .models import Cuenta, Transaccion

@transaction.atomic
def operar(*, usuario, cuenta_id, tipo, monto, destino_id=None, descripcion=''):
    try:
        monto = Decimal(str(monto))
    except (InvalidOperation, ValueError):
        raise ValidationError('Monto inválido.')
    if not monto.is_finite() or monto <= 0 or monto >= Decimal('1000000000000') or monto.as_tuple().exponent < -2:
        raise ValidationError('Use un monto positivo con máximo dos decimales y doce dígitos enteros.')
    if tipo not in dict(Transaccion.TIPOS):
        raise ValidationError('Tipo inválido.')
    if tipo == 'transferencia' and (not destino_id or int(destino_id) == int(cuenta_id)):
        raise ValidationError('Seleccione una cuenta de destino diferente.')
    if tipo != 'transferencia' and destino_id:
        raise ValidationError('Solo una transferencia admite destino.')
    ids = [cuenta_id] + ([destino_id] if destino_id else [])
    cuentas = {c.pk: c for c in Cuenta.objects.select_for_update().filter(pk__in=ids).order_by('pk')}
    cuenta = cuentas.get(int(cuenta_id))
    if cuenta is None or cuenta.cliente.usuario_id != usuario.pk:
        raise ValidationError('La cuenta no pertenece al usuario.')
    destino = cuentas.get(int(destino_id)) if destino_id else None
    if destino_id and destino is None:
        raise ValidationError('La cuenta de destino no existe.')
    limite = Decimal('999999999999.99')
    if tipo == 'deposito':
        changed = Cuenta.objects.filter(pk=cuenta.pk, saldo__lte=limite-monto).update(saldo=F('saldo')+monto)
        if not changed:
            raise ValidationError('Se excedería el saldo máximo.')
    else:
        changed = Cuenta.objects.filter(pk=cuenta.pk, saldo__gte=monto).update(saldo=F('saldo')-monto)
        if not changed:
            raise ValidationError('Saldo insuficiente.')
        if destino:
            changed = Cuenta.objects.filter(pk=destino.pk, saldo__lte=limite-monto).update(saldo=F('saldo')+monto)
            if not changed:
                raise ValidationError('El destino excedería el saldo máximo.')
    movimiento = Transaccion(cuenta=cuenta, destino=destino, tipo=tipo, monto=monto, descripcion=descripcion)
    movimiento.full_clean()
    movimiento.save()
    return movimiento
