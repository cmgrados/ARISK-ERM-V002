from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView, View
from django.apps import apps
from django.forms import modelform_factory
from django.contrib import messages
from django import forms

def catalog_index(request):
    """
    Vista principal que lista todos los catálogos disponibles usando tarjetas.
    """
    catalog_models = [
        {'name': 'Company', 'icon': 'fas fa-building', 'desc': 'Razón Social, RUC y oficina principal.'},
        {'name': 'Site', 'icon': 'fas fa-map-marker-alt', 'desc': 'Agencias, códigos, direcciones y responsables.'},
        {'name': 'OrganizationalUnit', 'icon': 'fas fa-sitemap', 'desc': 'Unidades de área y dependencias.'},
        {'name': 'Position', 'icon': 'fas fa-id-badge', 'desc': 'Catálogo de cargos para usuarios.'},
        {'name': 'Process', 'icon': 'fas fa-project-diagram', 'desc': 'Procesos principales del mapa.'},
        {'name': 'Subprocess', 'icon': 'fas fa-cog', 'desc': 'Subprocesos enlazados a procesos padre.'},
        {'name': 'Product', 'icon': 'fas fa-box-open', 'desc': 'Productos ofrecidos y configuraciones.'},
        {'name': 'RiskType', 'icon': 'fas fa-exclamation-triangle', 'desc': 'Tipos de riesgo (Operacional, etc).'},
        {'name': 'Parameter', 'icon': 'fas fa-sliders-h', 'desc': 'Parámetros del sistema y variables.'},
        {'name': 'SystemIntegration', 'icon': 'fas fa-plug', 'desc': 'Configuración de APIs (Gemini, Drive, Calendar).'},
        {'name': 'AIModulePrompt', 'icon': 'fas fa-robot', 'desc': 'Prompts dinámicos de IA por módulo.'},
        {'name': 'RiskCatalog', 'icon': 'fas fa-book', 'desc': 'Catálogo global de riesgos predefinidos y aprendidos.'},
        {'name': 'RiskCategory', 'app': 'op_risk', 'icon': 'fas fa-list', 'desc': 'Categorías de Riesgo de Basilea.'},
        {'name': 'ProbabilityLevel', 'app': 'op_risk', 'icon': 'fas fa-chart-line', 'desc': 'Niveles de Probabilidad.'},
        {'name': 'ImpactLevel', 'app': 'op_risk', 'icon': 'fas fa-bullseye', 'desc': 'Niveles de Impacto.'},
        {'name': 'RiskStatus', 'app': 'op_risk', 'icon': 'fas fa-tasks', 'desc': 'Estados del flujo de Riesgo.'},
    ]
    
    context = []
    for c in catalog_models:
        app_label = c.get('app', 'catalogs')
        model = apps.get_model(app_label, c['name'])
        context.append({
            'model_name': c['name'].lower(),
            'verbose_name': model._meta.verbose_name.capitalize() if hasattr(model._meta.verbose_name, 'capitalize') else model._meta.verbose_name,
            'verbose_name_plural': model._meta.verbose_name_plural.capitalize() if hasattr(model._meta.verbose_name_plural, 'capitalize') else model._meta.verbose_name_plural,
            'icon': c['icon'],
            'desc': c['desc'],
        })
        
    return render(request, 'catalogs/catalog_index.html', {'catalogs': context, 'page_title': 'Catálogos y Parámetros'})

MODEL_APP_MAP = {
    'company': 'catalogs',
    'site': 'catalogs',
    'organizationalunit': 'catalogs',
    'position': 'catalogs',
    'process': 'catalogs',
    'subprocess': 'catalogs',
    'product': 'catalogs',
    'risktype': 'catalogs',
    'parameter': 'catalogs',
    'systemintegration': 'catalogs',
    'aimoduleprompt': 'catalogs',
    'riskcatalog': 'catalogs',
    'riskcategory': 'op_risk',
    'probabilitylevel': 'op_risk',
    'impactlevel': 'op_risk',
    'riskstatus': 'op_risk',
}

class GenericCatalogMixin:
    def get_model_class(self):
        model_name = self.kwargs['model_name'].lower()
        app_label = MODEL_APP_MAP.get(model_name, 'catalogs')
        return apps.get_model(app_label, model_name)

    def get_queryset(self):
        return self.get_model_class().objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model_class()
        context['model_name'] = self.kwargs['model_name'].lower()
        context['verbose_name'] = model._meta.verbose_name.capitalize() if hasattr(model._meta.verbose_name, 'capitalize') else model._meta.verbose_name
        context['verbose_name_plural'] = model._meta.verbose_name_plural.capitalize() if hasattr(model._meta.verbose_name_plural, 'capitalize') else model._meta.verbose_name_plural
        context['page_title'] = context['verbose_name_plural']
        return context

class GenericCatalogListView(GenericCatalogMixin, ListView):
    template_name = 'catalogs/catalog_list.html'
    context_object_name = 'objects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.get_model_class()
        
        fields = [f for f in model._meta.fields if f.name not in ('id',)]
        context['fields'] = fields
        
        # Prepare rows dynamically to avoid template limitations
        rows = []
        for obj in context['objects']:
            row = {'obj': obj, 'values': []}
            for f in fields:
                val = getattr(obj, f.name)
                # handle foreign keys nicely by converting to string
                if val and hasattr(val, '__str__') and not isinstance(val, (str, int, float, bool)):
                    val = str(val)
                elif type(val) == bool:
                    val = "Sí" if val else "No"
                row['values'].append(val)
            rows.append(row)
        
        context['rows'] = rows
        return context

class GenericCatalogCreateView(GenericCatalogMixin, CreateView):
    template_name = 'catalogs/catalog_form.html'
    
    def get_form_class(self):
        model = self.get_model_class()
        # Customizing widgets dynamically
        widgets = {}
        for f in model._meta.fields:
            if f.name != 'id':
                if type(f).__name__ in ('BooleanField', 'NullBooleanField'):
                    widgets[f.name] = forms.CheckboxInput(attrs={'class': 'custom-control-input'})
                elif type(f).__name__ in ('ImageField', 'FileField'):
                    widgets[f.name] = forms.ClearableFileInput(attrs={'class': 'form-control-file'})
                elif type(f).__name__ in ('ForeignKey', 'OneToOneField') or getattr(f, 'choices', None):
                    widgets[f.name] = forms.Select(attrs={'class': 'form-control'})
                elif type(f).__name__ == 'TextField':
                    widgets[f.name] = forms.Textarea(attrs={'class': 'form-control', 'rows': 6})
                else:
                    widgets[f.name] = forms.TextInput(attrs={'class': 'form-control'})
        
        fields_list = [f.name for f in model._meta.fields if f.name != 'id']
        if model.__name__ == 'Site' and 'company' in fields_list:
            fields_list.remove('company')
            
        return modelform_factory(model, fields=fields_list, widgets=widgets)

    def form_valid(self, form):
        if self.get_model_class().__name__ == 'Site':
            Company = apps.get_model('catalogs', 'Company')
            company = Company.objects.first()
            if company:
                form.instance.company = company
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f"¡{self.get_model_class()._meta.verbose_name.title()} creado con éxito!")
        return reverse('catalogs:catalog_list', kwargs={'model_name': self.kwargs['model_name']})

class GenericCatalogUpdateView(GenericCatalogMixin, UpdateView):
    template_name = 'catalogs/catalog_form.html'
    
    def get_form_class(self):
        model = self.get_model_class()
        widgets = {}
        for f in model._meta.fields:
            if f.name != 'id':
                if type(f).__name__ in ('BooleanField', 'NullBooleanField'):
                    widgets[f.name] = forms.CheckboxInput(attrs={'class': 'custom-control-input'})
                elif type(f).__name__ in ('ImageField', 'FileField'):
                    widgets[f.name] = forms.ClearableFileInput(attrs={'class': 'form-control-file'})
                elif type(f).__name__ in ('ForeignKey', 'OneToOneField'):
                    widgets[f.name] = forms.Select(attrs={'class': 'form-control'})
                else:
                    widgets[f.name] = forms.TextInput(attrs={'class': 'form-control'})
        
        fields_list = [f.name for f in model._meta.fields if f.name != 'id']
        if model.__name__ == 'Site' and 'company' in fields_list:
            fields_list.remove('company')
            
        return modelform_factory(model, fields=fields_list, widgets=widgets)

    def get_success_url(self):
        messages.success(self.request, f"¡{self.get_model_class()._meta.verbose_name.title()} actualizado con éxito!")
        return reverse('catalogs:catalog_list', kwargs={'model_name': self.kwargs['model_name']})

from django.db import IntegrityError

class GenericCatalogBulkDeleteView(GenericCatalogMixin, View):
    def post(self, request, *args, **kwargs):
        selected_ids = request.POST.getlist('selected_ids')
        if selected_ids:
            model = self.get_model_class()
            try:
                count, _ = model.objects.filter(id__in=selected_ids).delete()
                messages.success(request, f"Se eliminaron {count} registros exitosamente.")
            except IntegrityError:
                messages.error(request, "No se pueden eliminar algunos registros seleccionados porque están siendo utilizados o tienen dependencias asociadas.")
        else:
            messages.warning(request, "No se seleccionó ningún registro para eliminar.")
        return redirect('catalogs:catalog_list', model_name=self.kwargs['model_name'])
