from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Perspectiva, ObjetivoEstrategico, Indicador, MetaPeriodo
from .serializers import PerspectivaSerializer, ObjetivoEstrategicoSerializer, IndicadorSerializer, MetaPeriodoSerializer
from .services import BSCCalculationEngine

class PerspectivaViewSet(viewsets.ModelViewSet):
    serializer_class = PerspectivaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # El TenantMiddleware ya debería estar filtrando, pero DRF recomienda usar explícitamente
        if hasattr(self.request.user, 'organization'):
            return Perspectiva.objects.filter(organization=self.request.user.organization)
        return Perspectiva.objects.none()

class ObjetivoEstrategicoViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetivoEstrategicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return ObjetivoEstrategico.objects.filter(organization=self.request.user.organization)
        return ObjetivoEstrategico.objects.none()

class IndicadorViewSet(viewsets.ModelViewSet):
    serializer_class = IndicadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return Indicador.objects.filter(organization=self.request.user.organization)
        return Indicador.objects.none()

class MetaPeriodoViewSet(viewsets.ModelViewSet):
    serializer_class = MetaPeriodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return MetaPeriodo.objects.filter(indicador__organization=self.request.user.organization)
        return MetaPeriodo.objects.none()

    def perform_create(self, serializer):
        # Instanciar pero no guardar aún en DB
        instance = serializer.save()
        # Procesar cálculos (porcentaje y semáforo)
        instance = BSCCalculationEngine.process_meta_periodo(instance)
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance = BSCCalculationEngine.process_meta_periodo(instance)
        instance.save()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class BulkMetasPlaneadasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            organization = request.user.organization if hasattr(request.user, 'organization') else None
            
            if not organization:
                return Response({"status": "error", "message": "Usuario no tiene organización asignada."}, status=status.HTTP_400_BAD_REQUEST)
                
            for row in data:
                persp_name = row.get('perspectiva', '').upper().replace('/', '_').replace(' ', '_')
                
                # Mapeo simple de nombres a choices
                tipo_persp = 'FINANCIERA'
                if 'CLIENTE' in persp_name or 'SOCIO' in persp_name:
                    tipo_persp = 'SOCIOS_CLIENTES'
                elif 'PROCESO' in persp_name:
                    tipo_persp = 'PROCESOS'
                elif 'APRENDIZAJE' in persp_name:
                    tipo_persp = 'APRENDIZAJE'

                perspectiva, _ = Perspectiva.objects.get_or_create(
                    organization=organization,
                    nombre=tipo_persp
                )
                
                obj_nombre = row.get('objetivo', 'Objetivo sin nombre')
                tipo_obj = row.get('tipo', 'Estratégico')
                area_resp = row.get('area', '')
                responsable = row.get('responsable', '')
                
                objetivo, _ = ObjetivoEstrategico.objects.get_or_create(
                    organization=organization,
                    perspectiva=perspectiva,
                    nombre=obj_nombre,
                    defaults={
                        'codigo': f'OBJ-{ObjetivoEstrategico.objects.filter(organization=organization).count() + 1}',
                        'tipo_objetivo': tipo_obj,
                        'area_responsable': area_resp,
                        'responsable': responsable
                    }
                )
                
                # Update existing objective if fields changed
                if not _:
                    objetivo.tipo_objetivo = tipo_obj
                    objetivo.area_responsable = area_resp
                    objetivo.responsable = responsable
                    objetivo.save()
                
                ind_nombre = row.get('indicador', 'Indicador')
                linea_base = row.get('base', '0').replace('%', '').strip()
                try: linea_base = float(linea_base)
                except: linea_base = 0

                indicador, _ = Indicador.objects.get_or_create(
                    organization=organization,
                    objetivo=objetivo,
                    nombre=ind_nombre,
                    defaults={
                        'unidad_medida': '%',
                        'frecuencia_medicion': 'ANUAL',
                        'linea_base': linea_base
                    }
                )
                
                # Crear o actualizar metas 1, 2, 3
                for i in range(1, 4):
                    meta_val = row.get(f'meta{i}', '0').replace('%', '').strip()
                    try: meta_val = float(meta_val)
                    except: continue # Si no es un numero valido, ignorar
                    
                    meta, _ = MetaPeriodo.objects.update_or_create(
                        indicador=indicador,
                        periodo=f'Meta {i}',
                        defaults={'meta_programada': meta_val}
                    )
                    
            return Response({"status": "success", "message": "Guardado correctamente"})
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from .models import ProyectoIniciativa, EjecucionPresupuestaria, HitoProyecto
from .serializers import ProyectoIniciativaSerializer, EjecucionPresupuestariaSerializer, HitoProyectoSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

class ProyectoIniciativaViewSet(viewsets.ModelViewSet):
    serializer_class = ProyectoIniciativaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return ProyectoIniciativa.objects.filter(organization=self.request.user.organization)
        return ProyectoIniciativa.objects.none()

class EjecucionPresupuestariaViewSet(viewsets.ModelViewSet):
    serializer_class = EjecucionPresupuestariaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return EjecucionPresupuestaria.objects.filter(proyecto__organization=self.request.user.organization)
        return EjecucionPresupuestaria.objects.none()

    def _handle_save(self, serializer):
        try:
            instance = serializer.save()
            instance.proyecto.actualizar_avances()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e))

    def perform_create(self, serializer):
        self._handle_save(serializer)

    def perform_update(self, serializer):
        self._handle_save(serializer)

class HitoProyectoViewSet(viewsets.ModelViewSet):
    serializer_class = HitoProyectoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'organization'):
            return HitoProyecto.objects.filter(proyecto__organization=self.request.user.organization)
        return HitoProyecto.objects.none()

    def _handle_save(self, serializer):
        try:
            instance = serializer.save()
            instance.proyecto.actualizar_avances()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e))

    def perform_create(self, serializer):
        self._handle_save(serializer)

    def perform_update(self, serializer):
        self._handle_save(serializer)

from .services import DashboardService

class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            organization = request.user.organization if hasattr(request.user, 'organization') else None
            if not organization:
                return Response({"status": "error", "message": "Organización no encontrada para este usuario."}, status=status.HTTP_400_BAD_REQUEST)
            
            data = DashboardService.get_dashboard_summary(organization)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
