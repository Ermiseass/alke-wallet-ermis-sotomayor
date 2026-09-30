import csv
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView, FormView
from .models import Cliente, Cuenta
from .forms import RegistroForm, ClienteForm, CuentaForm, OperacionForm
from .services import operar
from .queries import movimientos_usuario, resumen_cuentas, resumen_tipos, cuentas_con_saldo_sql

class RegistroView(FormView):
    template_name = 'form.html'
    form_class = RegistroForm
    success_url = reverse_lazy('inicio')
    extra_context = {'titulo': 'Crear mi perfil'}
    @transaction.atomic
    def form_valid(self, form):
        usuario = form.save()
        Cliente.objects.create(usuario=usuario, nombre=form.cleaned_data['nombre'], email=form.cleaned_data['email'])
        login(self.request, usuario)
        return super().form_valid(form)

class InicioView(LoginRequiredMixin, TemplateView):
    template_name = 'inicio.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuentas = Cuenta.objects.filter(cliente__usuario=self.request.user)
        context.update(cuentas=cuentas, saldo=cuentas.aggregate(total=Sum('saldo'))['total'] or 0,
                       movimientos=movimientos_usuario(self.request.user)[:5])
        return context

class PerfilView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    extra_context = {'titulo': 'Editar mi perfil y contactos'}
    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)

class PerfilDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('login')
    def get_queryset(self):
        return Cliente.objects.filter(usuario=self.request.user)
    def form_valid(self, form):
        if self.object.cuentas.exists():
            form.add_error(None, 'Elimine primero las cuentas sin movimientos. Los registros con historial se conservan.')
            return self.form_invalid(form)
        with transaction.atomic():
            usuario = self.object.usuario
            self.object.delete()
            usuario.delete()
        return HttpResponseRedirect(self.success_url)

class CuentaPropiaMixin(LoginRequiredMixin):
    model = Cuenta
    def get_queryset(self):
        return Cuenta.objects.filter(cliente__usuario=self.request.user)
class CuentaListView(CuentaPropiaMixin, ListView):
    template_name = 'cuentas.html'
class CuentaDetailView(CuentaPropiaMixin, DetailView):
    template_name = 'cuenta_detail.html'
class CuentaCreateView(CuentaPropiaMixin, CreateView):
    form_class = CuentaForm
    template_name = 'form.html'
    success_url = reverse_lazy('cuentas')
    extra_context = {'titulo': 'Nueva cuenta'}
    def form_valid(self, form):
        cliente = Cliente.objects.filter(usuario=self.request.user).first()
        if not cliente:
            form.add_error(None, 'Este usuario no tiene perfil de cliente. Regístrese desde Crear perfil.')
            return self.form_invalid(form)
        form.instance.cliente = cliente
        return super().form_valid(form)
class CuentaUpdateView(CuentaPropiaMixin, UpdateView):
    form_class = CuentaForm
    template_name = 'form.html'
    success_url = reverse_lazy('cuentas')
    extra_context = {'titulo': 'Editar cuenta'}
class CuentaDeleteView(CuentaPropiaMixin, DeleteView):
    template_name = 'confirm_delete.html'
    success_url = reverse_lazy('cuentas')
    def form_valid(self, form):
        if self.object.saldo != 0 or self.object.movimientos.exists() or self.object.recibidos.exists():
            form.add_error(None, 'Solo se eliminan cuentas vacías y sin historial de movimientos.')
            return self.form_invalid(form)
        return super().form_valid(form)

class OperacionView(LoginRequiredMixin, FormView):
    form_class = OperacionForm
    template_name = 'form.html'
    success_url = reverse_lazy('movimientos')
    extra_context = {'titulo': 'Realizar una operación', 'nota': 'Simulación académica: los depósitos y retiros no mueven dinero real.'}
    def get_form_kwargs(self):
        return {**super().get_form_kwargs(), 'usuario': self.request.user}
    def form_valid(self, form):
        d = form.cleaned_data
        try:
            operar(usuario=self.request.user, cuenta_id=d['cuenta'].pk, tipo=d['tipo'], monto=d['monto'],
                   destino_id=d.get('destino_id'), descripcion=d['descripcion'])
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)
        messages.success(self.request, 'Operación registrada correctamente.')
        return super().form_valid(form)

class MovimientosView(LoginRequiredMixin, ListView):
    template_name = 'movimientos.html'
    paginate_by = 20
    def get_queryset(self):
        qs = movimientos_usuario(self.request.user)
        tipo = self.request.GET.get('tipo', '')
        return qs.filter(tipo=tipo) if tipo else qs
class ReporteView(LoginRequiredMixin, TemplateView):
    template_name = 'reporte.html'
    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), 'resumen': resumen_cuentas(self.request.user),
                'tipos': resumen_tipos(self.request.user), 'sql': list(cuentas_con_saldo_sql(self.request.user))}
class ExportarView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="movimientos.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Tipo', 'Monto CLP', 'Referencia'])
        for m in movimientos_usuario(request.user):
            writer.writerow([m.creada.isoformat(), m.get_tipo_display(), m.monto, m.referencia])
        return response
