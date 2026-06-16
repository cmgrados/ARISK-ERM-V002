from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Perspectiva, ObjetivoEstrategico, Indicador, MetaPeriodo
from .serializers import PerspectivaSerializer, ObjetivoEstrategicoSerializer, IndicadorSerializer, MetaPeriodoSerializer
from .services import BSCCalculationEngine

class PerspectivaViewSet(viewsets.ModelViewSet):
    serializer_class = PerspectivaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            return Perspectiva.objects.filter(organization=user_org)
        return Perspectiva.objects.none()

class ObjetivoEstrategicoViewSet(viewsets.ModelViewSet):
    serializer_class = ObjetivoEstrategicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            return ObjetivoEstrategico.objects.filter(organization=user_org)
        return ObjetivoEstrategico.objects.none()

class IndicadorViewSet(viewsets.ModelViewSet):
    serializer_class = IndicadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            return Indicador.objects.filter(organization=user_org)
        return Indicador.objects.none()

class MetaPeriodoViewSet(viewsets.ModelViewSet):
    serializer_class = MetaPeriodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            return MetaPeriodo.objects.filter(indicador__organization=user_org)
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

from .models import ProyectoIniciativa, EjecucionPresupuestaria, HitoProyecto, PortafolioPOA, ActividadPOA
from .serializers import ProyectoIniciativaSerializer, EjecucionPresupuestariaSerializer, HitoProyectoSerializer, PortafolioPOASerializer, ActividadPOASerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

class PortafolioPOAViewSet(viewsets.ModelViewSet):
    serializer_class = PortafolioPOASerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
            
        if user_org:
            queryset = PortafolioPOA.objects.filter(organization=user_org)
            plan_id = self.request.query_params.get('plan_id')
            if plan_id:
                queryset = queryset.filter(estrategia__plan_id=plan_id)
            elif 'active_strategic_plan_id' in self.request.session:
                queryset = queryset.filter(estrategia__plan_id=self.request.session.get('active_strategic_plan_id'))
                
            anio = self.request.query_params.get('anio')
            if anio:
                queryset = queryset.filter(anio=anio)
                
            return queryset
        return PortafolioPOA.objects.none()

    def perform_create(self, serializer):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if not user_org:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "El usuario no tiene una organización asignada. No se puede crear el registro."})
            
        nombre_proyecto = serializer.validated_data.get('nombre_proyecto')
        anio = serializer.validated_data.get('anio')
        
        if PortafolioPOA.objects.filter(organization=user_org, nombre_proyecto=nombre_proyecto, anio=anio).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": f"Ya existe un proyecto con el nombre '{nombre_proyecto}' para el año {anio}."})
            
        serializer.save(organization=user_org)

    def perform_update(self, serializer):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
            
        nombre_proyecto = serializer.validated_data.get('nombre_proyecto', serializer.instance.nombre_proyecto)
        anio = serializer.validated_data.get('anio', serializer.instance.anio)
        
        if PortafolioPOA.objects.exclude(pk=serializer.instance.pk).filter(organization=user_org, nombre_proyecto=nombre_proyecto, anio=anio).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": f"Ya existe un proyecto con el nombre '{nombre_proyecto}' para el año {anio}."})
            
        serializer.save()

class ActividadPOAViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadPOASerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
            
        if user_org:
            queryset = ActividadPOA.objects.filter(organization=user_org)
            proyecto_id = self.request.query_params.get('proyecto_id')
            if proyecto_id:
                queryset = queryset.filter(proyecto_id=proyecto_id)
            else:
                plan_id = self.request.query_params.get('plan_id')
                if plan_id:
                    queryset = queryset.filter(proyecto__estrategia__plan_id=plan_id)
                elif 'active_strategic_plan_id' in self.request.session:
                    queryset = queryset.filter(proyecto__estrategia__plan_id=self.request.session.get('active_strategic_plan_id'))
            return queryset
        return ActividadPOA.objects.none()

    def perform_create(self, serializer):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        serializer.save(organization=user_org)

class ProyectoIniciativaViewSet(viewsets.ModelViewSet):
    serializer_class = ProyectoIniciativaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            queryset = ProyectoIniciativa.objects.filter(organization=user_org)
            plan_id = self.request.query_params.get('plan_id')
            if plan_id:
                queryset = queryset.filter(indicador__objetivo__perspectiva__plan_id=plan_id)
            elif 'active_strategic_plan_id' in self.request.session:
                queryset = queryset.filter(indicador__objetivo__perspectiva__plan_id=self.request.session.get('active_strategic_plan_id'))
            return queryset
        return ProyectoIniciativa.objects.none()

    def perform_create(self, serializer):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if not user_org:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "El usuario no tiene una organización asignada."})
        serializer.save(organization=user_org)

class EjecucionPresupuestariaViewSet(viewsets.ModelViewSet):
    serializer_class = EjecucionPresupuestariaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            queryset = EjecucionPresupuestaria.objects.filter(proyecto__organization=user_org)
            plan_id = self.request.query_params.get('plan_id')
            if plan_id:
                queryset = queryset.filter(proyecto__indicador__objetivo__perspectiva__plan_id=plan_id)
            elif 'active_strategic_plan_id' in self.request.session:
                queryset = queryset.filter(proyecto__indicador__objetivo__perspectiva__plan_id=self.request.session.get('active_strategic_plan_id'))
            return queryset
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
        user_org = getattr(self.request.user, 'organization', None)
        if not user_org:
            from users.models import Organization
            user_org = Organization.objects.first()
        if user_org:
            queryset = HitoProyecto.objects.filter(proyecto__organization=user_org)
            plan_id = self.request.query_params.get('plan_id')
            if plan_id:
                queryset = queryset.filter(proyecto__indicador__objetivo__perspectiva__plan_id=plan_id)
            elif 'active_strategic_plan_id' in self.request.session:
                queryset = queryset.filter(proyecto__indicador__objetivo__perspectiva__plan_id=self.request.session.get('active_strategic_plan_id'))
            return queryset
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
