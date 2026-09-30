from django.urls import path
from . import views as v
urlpatterns = [path('', v.InicioView.as_view(), name='inicio'), path('registro/', v.RegistroView.as_view(), name='registro'),
    path('perfil/<int:pk>/editar/', v.PerfilView.as_view(), name='perfil'),
    path('perfil/<int:pk>/eliminar/', v.PerfilDeleteView.as_view(), name='perfil_eliminar'),
    path('cuentas/', v.CuentaListView.as_view(), name='cuentas'), path('cuentas/nueva/', v.CuentaCreateView.as_view(), name='cuenta_crear'),
    path('cuentas/<int:pk>/', v.CuentaDetailView.as_view(), name='cuenta_detalle'),
    path('cuentas/<int:pk>/editar/', v.CuentaUpdateView.as_view(), name='cuenta_editar'),
    path('cuentas/<int:pk>/eliminar/', v.CuentaDeleteView.as_view(), name='cuenta_eliminar'),
    path('operar/', v.OperacionView.as_view(), name='operar'), path('movimientos/', v.MovimientosView.as_view(), name='movimientos'),
    path('reportes/', v.ReporteView.as_view(), name='reportes'), path('reportes/csv/', v.ExportarView.as_view(), name='exportar')]
