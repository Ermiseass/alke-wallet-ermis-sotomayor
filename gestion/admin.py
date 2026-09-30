from django.contrib import admin
from .models import Cliente, Cuenta, Transaccion
admin.site.site_header = 'Alke Wallet | Administración'
admin.site.site_title = 'Alke Wallet'
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'telefono']
    search_fields = ['nombre', 'email']
    filter_horizontal = ['contactos']
@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ['alias', 'cliente', 'saldo', 'numero']
    readonly_fields = ['saldo', 'numero', 'creada']
@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['referencia', 'tipo', 'cuenta', 'destino', 'monto', 'creada']
    list_filter = ['tipo']
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
