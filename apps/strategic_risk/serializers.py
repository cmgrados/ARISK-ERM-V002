from rest_framework import serializers
from .models import Perspectiva, ObjetivoEstrategico, Indicador, MetaPeriodo
from .services import BSCCalculationEngine

class MetaPeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaPeriodo
        fields = ['id', 'periodo', 'meta_programada', 'resultado_real', 'porcentaje_cumplimiento', 'semaforo']
        read_only_fields = ['porcentaje_cumplimiento', 'semaforo']

    def validate(self, data):
        # Para asignar la organización (heredado del ModelSerializer y ViewSet, pero a nivel de servicio):
        # Aquí no es necesario si se guarda desde el ViewSet, pero podemos forzar cálculo
        return data

class IndicadorSerializer(serializers.ModelSerializer):
    metas_periodo = MetaPeriodoSerializer(many=True, read_only=True)

    class Meta:
        model = Indicador
        fields = ['id', 'nombre', 'formula', 'unidad_medida', 'frecuencia_medicion', 'linea_base', 'meta_final', 'metas_periodo']

class ObjetivoEstrategicoSerializer(serializers.ModelSerializer):
    indicadores = IndicadorSerializer(many=True, read_only=True)

    class Meta:
        model = ObjetivoEstrategico
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'indicadores']

class PerspectivaSerializer(serializers.ModelSerializer):
    objetivos = ObjetivoEstrategicoSerializer(many=True, read_only=True)

    class Meta:
        model = Perspectiva
        fields = ['id', 'nombre', 'descripcion', 'peso_porcentual', 'objetivos']

from .models import ProyectoIniciativa, EjecucionPresupuestaria, HitoProyecto, PortafolioPOA, ActividadPOA

class ActividadPOASerializer(serializers.ModelSerializer):
    class Meta:
        model = ActividadPOA
        fields = '__all__'
        read_only_fields = ['organization']

class PortafolioPOASerializer(serializers.ModelSerializer):
    actividades = ActividadPOASerializer(many=True, read_only=True)
    estrategia_desc = serializers.SerializerMethodField()

    class Meta:
        model = PortafolioPOA
        fields = '__all__'
        read_only_fields = ['organization']

    def get_estrategia_desc(self, obj):
        return obj.estrategia.descripcion if obj.estrategia else None

class EjecucionPresupuestariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EjecucionPresupuestaria
        fields = '__all__'

class HitoProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HitoProyecto
        fields = '__all__'

class ProyectoIniciativaSerializer(serializers.ModelSerializer):
    ejecuciones = EjecucionPresupuestariaSerializer(many=True, read_only=True)
    hitos = HitoProyectoSerializer(many=True, read_only=True)

    class Meta:
        model = ProyectoIniciativa
        fields = '__all__'
        read_only_fields = ['porcentaje_avance_fisico', 'porcentaje_avance_financiero', 'semaforo_ejecucion']
