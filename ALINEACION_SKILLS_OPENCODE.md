# 📊 ALINEACIÓN CON SKILLS PYTHON/DJANGO

**Análisis:** Cómo el proyecto A.RISK ERM V2 se alinea con las mejores prácticas de `skills-opencode`.

**Fecha:** 2026-08-03

---

## 🟢 LO QUE YA HACES BIEN

### Python - Code Style & PEP 8
- ✅ `snake_case` en funciones y variables
- ✅ `CamelCase` en clases (User, Organization, etc.)
- ✅ Estructura básica de proyecto en `apps/`

### Django - Project Structure
- ✅ **Carpeta `apps/`** - Bien organizada (25 apps temáticas)
- ✅ **Apps atómicas** - Cada app es responsable de su dominio (risks, users, controls, etc.)
- ✅ **AppConfig definidos** - Cada app tiene apps.py

### Django - Models
- ✅ `__str__` definidos en modelos
- ✅ `Meta.verbose_name` en algunos modelos
- ✅ `created_at` y `updated_at` en modelos principales
- ✅ Campos `is_active`/soft delete considerados

### Django - Security
- ✅ CSRF habilitado por defecto
- ✅ Middleware de seguridad activo
- ✅ Custom User model (`AbstractUser`)
- ✅ Permiso-based access (es_auditor, es_risk_manager)

---

## 🟡 LO QUE NECESITA MEJORA (ALTA PRIORIDAD)

### Python - Type Hints
**Estado:** ❌ No usados

**Impacto:** Bajo (funciona sin ellos, pero código difícil de mantener)

**Ejemplos de mejora:**
```python
# Antes (sin tipos)
def get_risk_metrics(risk_id):
    risk = Risk.objects.get(id=risk_id)
    return risk.metrics

# Después (con tipos)
from typing import Optional
from apps.risks.models import Risk, RiskMetric

def get_risk_metrics(risk_id: int) -> Optional[list[RiskMetric]]:
    risk = Risk.objects.get(id=risk_id)
    return risk.metrics
```

**Plan:** Fase 3 - Implementar tipos progresivamente (empezar por APIs/serializers)

---

### Python - Logging
**Estado:** ❌ No implementado (hay 37 `print()` statements)

**Impacto:** Alto (imposible debuggear en producción)

**Necesario:**
```python
import logging

logger = logging.getLogger(__name__)

# En lugar de:
print("User created:", user.id)

# Hacer:
logger.info(f"User created: {user.id}")
```

**Plan:** Fase 2 - Reemplazar todos los `print()` con logging

---

### Python - Testing
**Estado:** ❌ 0% cobertura

**Impacto:** CRÍTICA (sin tests no puedes refactorizar con confianza)

**Necesario:**
- pytest + pytest-django
- FactoryBoy para datos de prueba
- Fixtures en conftest.py
- Cobertura mínima 80%

**Plan:** Fase 2 - Implementar pytest desde cero

---

### Python - Error Handling
**Estado:** 🟡 Parcial

**Problemas encontrados:**
- Bare `except:` en algunos lugares
- Bare `except Exception:` demasiado amplio
- No hay excepciones personalizadas del dominio

**Necesario:**
```python
class DomainError(Exception):
    """Base de todas las excepciones del dominio."""

class RiskNotFoundError(DomainError):
    pass

# Uso
try:
    risk = Risk.objects.get(id=risk_id)
except Risk.DoesNotExist as e:
    raise RiskNotFoundError(f"Risk {risk_id} not found") from e
```

**Plan:** Fase 3 - Crear excepciones por dominio

---

### Django - DRF Integration
**Estado:** 🟡 Parcial (views básicas, pero no DRF)

**Problema:** Views son function-based (FBV), no DRF ViewSets

**Impacto:** No hay API formal, no hay serializers, no hay schema OpenAPI

**Necesario:**
- Migrar a `ViewSets` + `Serializers`
- Implementar DRF routing automático
- Schema OpenAPI con `drf-spectacular`
- Permisos DRF (`IsAuthenticated`, personalizados)

**Plan:** Fase 2-3 - Refactorizar a DRF

---

### Django - Settings Management
**Estado:** ✅ **YA IMPLEMENTADO EN FASE 1**

Con Pydantic ya tienes:
- ✅ Variables de entorno
- ✅ Separación por entorno
- ✅ Validación automática
- ✅ Type safety

**No necesita cambios.**

---

### Django - Performance
**State:** 🟡 Riesgo alto

**Problemas potenciales:**
- 465 MB SQLite (acumulación de datos)
- `.values()` → `list()` en views (carga todo a memoria)
- Sin `select_related()` / `prefetch_related()`
- Sin indexación de base de datos
- Sin paginación documentada

**Plan:** Fase 3 - Auditoría de queries con django-debug-toolbar

---

## 🔴 LO QUE FALTA (BAJA PRIORIDAD)

### Python - Async/Await
**Estado:** No usado

**Cuando usarlo:** Para APIs (FastAPI), no para Django tradicional

**Para A.RISK ERM:** No necesario por ahora (Django es sync)

---

### Python - Code Quality Tools
**Estado:** 🟡 Parcial

**Necesario:**
- **Ruff** - Linter ultra rápido
- **Black** - Formateador automático
- **mypy** - Type checking
- **pre-commit** - Hooks automáticos

**Plan:** Fase 3 - Setup de tooling en pyproject.toml

---

## 📋 ROADMAP ALINEACIÓN CON SKILLS

### Fase 1 (YA HECHO) ✅
- [x] Pydantic Settings
- [x] Remover .env del historio de Git
- [x] Documentación de seguridad

### Fase 2 (PRÓXIMO: 1-2 semanas)
- [ ] **Pytest + pytest-django** - Cobertura mínima 20% en 3 apps críticas
- [ ] **Logging framework** - Reemplazar 37 `print()` statements
- [ ] **GitHub Actions CI/CD** - Ejecutar tests en cada push
- [ ] **DRF + Serializers** - En 3 endpoints principales

### Fase 3 (2-4 semanas)
- [ ] **Type Hints** - Progresivamente en nuevas funciones
- [ ] **Excepciones del dominio** - DomainError base + específicas
- [ ] **Performance audit** - django-debug-toolbar + N+1 fixes
- [ ] **Code Quality Tools** - Ruff, Black, mypy en pre-commit

### Fase 4 (Mantenimiento)
- [ ] Aumentar cobertura a 60%+
- [ ] Migrar más views a DRF
- [ ] OpenAPI schema completo
- [ ] Monitoreo en producción (Sentry)

---

## 🎯 PRIORIDAD INMEDIATA (Fase 2)

Enfócate en ESTOS TRES para máximo impacto:

### 1. **Pytest + Cobertura** 🧪
- **Impacto:** Previene regressions en refactoring futuro
- **Esfuerzo:** 2-3 días
- **Ganancia:** Confianza para cambiar código

### 2. **Logging** 📝
- **Impacto:** Debuggeable en producción
- **Esfuerzo:** 1 día
- **Ganancia:** Observabilidad

### 3. **DRF en endpoints críticos** 🚀
- **Impacto:** API formal, documentación automática
- **Esfuerzo:** 2-3 días
- **Ganancia:** Escalabilidad + reusabilidad

---

## 📚 Recursos

Todos los skills están en:
```
C:\Users\VICTUS\Desktop\skills-opencode\
├── python/SKILL.md      (268 líneas - Type Hints, Testing, Logging, etc.)
├── django/SKILL.md      (407 líneas - Models, DRF, Performance, etc.)
└── README.md
```

---

## ✅ Checklist para Fase 2

- [ ] Leer completo `python/SKILL.md` (enfoque: Testing + Logging)
- [ ] Leer completo `django/SKILL.md` (enfoque: DRF + Performance)
- [ ] Crear `tests/conftest.py` con fixtures base
- [ ] Implementar logging en `config/settings/base.py`
- [ ] Convertir 1 view simple a DRF como prueba de concepto
- [ ] GitHub Actions workflow para pytest

---

**Status:** 📊 Alineación 60% → Meta: 90% al finalizar Fase 3
