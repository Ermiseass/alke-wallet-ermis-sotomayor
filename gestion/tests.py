from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, Client
from django.urls import reverse
from .models import Cliente, Cuenta, Transaccion
from .services import operar
from .queries import resumen_cuentas, cuentas_con_saldo_sql, resumen_tipos


class WalletTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ermis', password='Prueba-Segura-2026')
        self.v = User.objects.create_user('otro', password='Prueba-Segura-2026')
        self.c = Cliente.objects.create(usuario=self.u, nombre='Ermis Sotomayor', email='ermis@example.com')
        self.d = Cliente.objects.create(usuario=self.v, nombre='Otro', email='otro@example.com')
        self.a = Cuenta.objects.create(cliente=self.c, alias='Principal')
        self.b = Cuenta.objects.create(cliente=self.d, alias='Destino')
        self.client.force_login(self.u)

    def op(self, tipo='deposito', monto='100.00', **kwargs):
        return operar(usuario=self.u, cuenta_id=self.a.pk, tipo=tipo, monto=monto, **kwargs)

    def test_deposito_y_retiro_exactos(self):
        self.op(monto='100.25')
        self.op('retiro', '10.10')
        self.a.refresh_from_db()
        self.assertEqual(self.a.saldo, Decimal('90.15'))

    def test_transferencia_conserva_total(self):
        self.op()
        self.op('transferencia', '35.20', destino_id=self.b.pk)
        self.a.refresh_from_db(); self.b.refresh_from_db()
        self.assertEqual(self.a.saldo, Decimal('64.80'))
        self.assertEqual(self.b.saldo, Decimal('35.20'))

    def test_saldo_insuficiente_no_crea_movimiento(self):
        with self.assertRaises(ValidationError):
            self.op('retiro', '1')
        self.assertEqual(Transaccion.objects.count(), 0)

    def test_transferencia_fallida_revierte_ambas_cuentas(self):
        self.op()
        Cuenta.objects.filter(pk=self.b.pk).update(saldo=Decimal('999999999999.99'))
        with self.assertRaises(ValidationError):
            self.op('transferencia', '20', destino_id=self.b.pk)
        self.a.refresh_from_db()
        self.assertEqual(self.a.saldo, Decimal('100'))
        self.assertEqual(Transaccion.objects.count(), 1)

    def test_montos_invalidos(self):
        for monto in ['0', '-1', '1.001', 'NaN', 'Infinity', 'texto', '1000000000000']:
            with self.subTest(monto=monto), self.assertRaises(ValidationError):
                self.op(monto=monto)

    def test_destinos_invalidos(self):
        for destino in [None, self.a.pk, 99999]:
            with self.subTest(destino=destino), self.assertRaises(ValidationError):
                self.op('transferencia', destino_id=destino)

    def test_operacion_ajena_rechazada(self):
        with self.assertRaises(ValidationError):
            operar(usuario=self.u, cuenta_id=self.b.pk, tipo='deposito', monto='100')

    def test_crud_de_cuenta(self):
        self.assertEqual(self.client.post(reverse('cuenta_crear'), {'alias': 'Nueva'}).status_code, 302)
        cuenta = Cuenta.objects.get(alias='Nueva')
        self.assertEqual(cuenta.cliente, self.c)
        self.assertEqual(self.client.get(reverse('cuenta_detalle', args=[cuenta.pk])).status_code, 200)
        self.client.post(reverse('cuenta_editar', args=[cuenta.pk]), {'alias': 'Editada', 'saldo': '9999'})
        cuenta.refresh_from_db()
        self.assertEqual(cuenta.alias, 'Editada'); self.assertEqual(cuenta.saldo, 0)
        self.assertEqual(self.client.post(reverse('cuenta_eliminar', args=[cuenta.pk])).status_code, 302)
        self.assertFalse(Cuenta.objects.filter(pk=cuenta.pk).exists())

    def test_no_accede_a_cuentas_ajenas(self):
        for nombre in ['cuenta_detalle', 'cuenta_editar', 'cuenta_eliminar']:
            self.assertEqual(self.client.get(reverse(nombre, args=[self.b.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('cuenta_editar', args=[self.b.pk]), {'alias': 'Ataque'}).status_code, 404)
        self.assertEqual(self.client.post(reverse('cuenta_eliminar', args=[self.b.pk])).status_code, 404)

    def test_no_borra_cuentas_con_historial(self):
        self.op(); self.op('retiro')
        response = self.client.post(reverse('cuenta_eliminar', args=[self.a.pk]))
        self.assertContains(response, 'sin historial')
        self.assertTrue(Cuenta.objects.filter(pk=self.a.pk).exists())

    def test_csrf_exigido(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.u)
        self.assertEqual(client.post(reverse('cuenta_crear'), {'alias': 'Sin token'}).status_code, 403)

    def test_login_requerido(self):
        self.client.logout()
        for url in ['/', '/cuentas/', '/operar/', '/reportes/', '/movimientos/', '/reportes/csv/']:
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_registro_y_perfil(self):
        self.client.logout()
        response = self.client.post(reverse('registro'), {'username': 'nuevo', 'nombre': 'Nuevo', 'email': 'nuevo@example.com',
            'password1': 'NuevaClave-Test-2026', 'password2': 'NuevaClave-Test-2026'})
        self.assertEqual(response.status_code, 302)
        perfil = Cliente.objects.get(email='nuevo@example.com')
        self.client.post(reverse('perfil', args=[perfil.pk]), {'nombre': 'Actualizado', 'email': 'nuevo@example.com', 'telefono': '+56912345678'})
        perfil.refresh_from_db(); self.assertEqual(perfil.nombre, 'Actualizado')
        self.client.post(reverse('perfil_eliminar', args=[perfil.pk]))
        self.assertFalse(User.objects.filter(username='nuevo').exists())

    def test_relaciones_y_consultas(self):
        self.c.contactos.add(self.d)
        self.assertEqual(self.c.contactos.get(), self.d)
        self.assertEqual(self.u.cliente, self.c)
        self.op(); self.op('retiro', '10')
        self.assertEqual(resumen_cuentas(self.u).get().operaciones, 2)
        self.assertEqual([c.pk for c in cuentas_con_saldo_sql(self.u)], [self.a.pk])
        self.assertEqual(len(list(resumen_tipos(self.u))), 2)

    def test_restricciones_en_base_datos(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cuenta.objects.filter(pk=self.a.pk).update(saldo=-1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Transaccion.objects.create(cuenta=self.a, tipo='deposito', monto=0)

    def test_paginas_y_csv(self):
        self.op()
        for nombre in ['inicio', 'cuentas', 'movimientos', 'reportes', 'operar']:
            self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)
        response = self.client.get(reverse('exportar'))
        self.assertContains(response, 'Monto CLP')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_formulario_transferencia_y_filtro(self):
        self.op()
        response = self.client.post(reverse('operar'), {'cuenta': self.a.pk, 'tipo': 'transferencia', 'monto': '40', 'destino_numero': str(self.b.numero), 'descripcion': 'Prueba web'})
        self.assertEqual(response.status_code, 302)
        self.b.refresh_from_db(); self.assertEqual(self.b.saldo, 40)
        response = self.client.get(reverse('movimientos'), {'tipo': 'transferencia'})
        self.assertEqual(len(response.context['object_list']), 1)

    def test_historial_privado_y_receptor(self):
        self.op()
        self.client.force_login(self.v)
        self.assertEqual(len(self.client.get(reverse('movimientos')).context['object_list']), 0)
        self.op('transferencia', '10', destino_id=self.b.pk)
        self.assertEqual(len(self.client.get(reverse('movimientos')).context['object_list']), 1)

    def test_admin_y_logout(self):
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        self.u.is_staff = self.u.is_superuser = True
        self.u.save()
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.assertEqual(self.client.post('/logout/').status_code, 302)

    def test_perfil_ajeno_no_editable(self):
        self.assertEqual(self.client.get(reverse('perfil', args=[self.d.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('perfil_eliminar', args=[self.d.pk])).status_code, 404)
