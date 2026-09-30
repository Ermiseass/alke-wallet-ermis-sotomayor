from django.db.models import Q, Count, Sum
from .models import Cuenta, Transaccion
def movimientos_usuario(usuario):
    return Transaccion.objects.filter(Q(cuenta__cliente__usuario=usuario) | Q(destino__cliente__usuario=usuario)).select_related('cuenta', 'destino')
def resumen_cuentas(usuario):
    return Cuenta.objects.filter(cliente__usuario=usuario).annotate(operaciones=Count('movimientos')).order_by('-saldo')
def cuentas_con_saldo_sql(usuario):
    # Parámetros separados: el dato no se interpola dentro del SQL.
    return Cuenta.objects.raw('SELECT c.* FROM gestion_cuenta c JOIN gestion_cliente cl ON c.cliente_id = cl.id WHERE cl.usuario_id = %s AND c.saldo > %s ORDER BY c.id', [usuario.pk, 0])
def resumen_tipos(usuario):
    return movimientos_usuario(usuario).exclude(descripcion__iexact='anulado').values('tipo').annotate(cantidad=Count('id'), volumen=Sum('monto')).order_by('tipo')
