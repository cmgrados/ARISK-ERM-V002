# 📋 FASE 3: TESTS + DRF - PLAN DETALLADO

**Objetivo:** Aumentar cobertura de tests + Implementar API profesional con DRF

**Duración:** 1-2 semanas  
**Prioridad:** Alta (Foundation para producción)

---

## 🎯 FASE 3a: TESTS REFINADOS (3 días)

### Meta: 30%+ cobertura en 3 apps críticas

#### **Paso 1: Ajustar Factories (2 horas)**

Modelos reales encontrados:

```python
# Organization
- name (CharField, unique)
- ruc (CharField, unique, nullable)
- is_active (BooleanField, default=True)
- created_at (DateTimeField, auto_now_add)

# User (extends AbstractUser)
- organization (ForeignKey, nullable)
- role (ForeignKey to Role, nullable)
- is_risk_manager (BooleanField)
- is_auditor (BooleanField)
- can_access_* flags (BooleanField)

# Role
- name (CharField, unique)
- description (TextField, nullable)
- permissions (JSONField)
```

**Tareas:**
- [ ] Crear RoleFactory
- [ ] Actualizar UserFactory con role
- [ ] Actualizar OrganizationFactory (remover description)
- [ ] Crear CreditOperationFactory (si modelo existe)

#### **Paso 2: Escribir Tests Unitarios (1 día)**

Archivos a actualizar:

**tests/test_users.py** - Cobertura esperada: 80%
```python
Tests para crear:
✓ User creation
✓ User password hashing
✓ User organization assignment
✓ User role assignment
✓ User permissions (is_risk_manager, is_auditor)
✓ User access flags
✓ Multiple users per organization
✓ Organization lifecycle
✓ Role creation
```

**tests/test_risks.py** - Cobertura esperada: 70%
```python
Tests para crear:
✓ Risk creation
✓ Risk update
✓ Risk deletion (soft delete con is_active)
✓ Risk filtering by organization
✓ Risk status transitions
✓ Multiple risks per organization
```

**tests/test_credit_risk.py** (NUEVO)
```python
Tests para crear:
✓ Customer creation
✓ CreditOperation creation
✓ Credit metrics calculation
✓ Credit status transitions
```

#### **Paso 3: Ejecutar Tests (2 horas)**

```bash
# Ejecutar con cobertura
pytest tests/ -v --cov=apps --cov-report=html

# Meta: 30%+ cobertura
# Ideal: 50%+ en apps críticas (users, risks, credit_risk)
```

---

## 🎯 FASE 3b: DRF INTEGRATION (4 días)

### Meta: API profesional con OpenAPI schema

#### **Paso 1: Crear Serializers (1 día)**

**Archivo:** `apps/users/serializers.py` (NUEVO)

```python
# Serializers para crear:

class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'ruc', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class UserSerializer(ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    organization_id = IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'organization', 'organization_id', 'is_risk_manager', 
            'is_auditor', 'is_active'
        ]
        read_only_fields = ['id']

class RoleSerializer(ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions']

class UserDetailSerializer(UserSerializer):
    role = RoleSerializer(read_only=True)
    # Versión detallada con más info
```

**Archivo:** `apps/risks/serializers.py` (NUEVO)

```python
class RiskSerializer(ModelSerializer):
    class Meta:
        model = Risk
        fields = [
            'id', 'name', 'description', 'status', 
            'organization', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

#### **Paso 2: Crear ViewSets (1.5 días)**

**Archivo:** `apps/users/viewsets.py` (NUEVO)

```python
class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Solo ver tu propia org
        if self.request.user.organization:
            return Organization.objects.filter(
                id=self.request.user.organization.id
            )
        return Organization.objects.none()

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['organization', 'is_active']
    search_fields = ['username', 'email', 'first_name']
    ordering_fields = ['created_at', 'username']
```

**Archivo:** `apps/risks/viewsets.py` (NUEVO)

```python
class RiskViewSet(ModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'organization']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
```

#### **Paso 3: Setup Routing (1.5 días)**

**Archivo:** `config/urls.py` (MODIFICAR)

```python
from rest_framework.routers import DefaultRouter
from apps.users.viewsets import UserViewSet, OrganizationViewSet
from apps.risks.viewsets import RiskViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet)
router.register(r'users', UserViewSet)
router.register(r'risks', RiskViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    # ... resto de urls
]
```

#### **Paso 4: Agregar OpenAPI Schema (1 hora)**

```bash
# Instalar
pip install drf-spectacular

# En settings.py INSTALLED_APPS:
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

# En settings.py REST_FRAMEWORK:
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# En urls.py:
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]
```

#### **Paso 5: Escribir Tests de API (1 día)**

**Archivo:** `tests/test_api.py` (NUEVO)

```python
@pytest.mark.django_db
class TestUsersAPI:
    def test_list_users(self, api_client, user_with_org):
        response = api_client.get('/api/v1/users/')
        assert response.status_code == 401  # Sin auth
        
    def test_list_users_authenticated(self, authenticated_api_client):
        response = authenticated_api_client.get('/api/v1/users/')
        assert response.status_code == 200
        
    def test_create_user(self, authenticated_api_client):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'pass123456'
        }
        response = authenticated_api_client.post('/api/v1/users/', data)
        assert response.status_code in [201, 403]  # Depende de permisos

@pytest.mark.django_db
class TestRisksAPI:
    def test_list_risks(self, authenticated_api_client, risk):
        response = authenticated_api_client.get('/api/v1/risks/')
        assert response.status_code == 200
        
    def test_create_risk(self, authenticated_api_client, organization):
        data = {
            'name': 'New Risk',
            'description': 'Test',
            'organization': organization.id
        }
        response = authenticated_api_client.post('/api/v1/risks/', data)
        assert response.status_code == 201
```

---

## 🎯 FASE 3c: POLISH (1 día)

- [ ] Agregar type hints
- [ ] Validaciones en serializers
- [ ] Filtrado avanzado
- [ ] Paginación
- [ ] Rate limiting

---

## 📊 CHECKLIST FASE 3

### 3a: Tests
- [ ] Factories ajustadas (RoleFactory, CreditOperationFactory)
- [ ] tests/test_users.py completo
- [ ] tests/test_risks.py completo
- [ ] tests/test_credit_risk.py (NUEVO)
- [ ] Cobertura 30%+ (Target: 50%+)
- [ ] Todos los tests pasando

### 3b: DRF
- [ ] Serializers (users, risks, credit_risk)
- [ ] ViewSets (organizations, users, risks)
- [ ] Routing con DefaultRouter
- [ ] Permisos configurados (IsAuthenticated)
- [ ] OpenAPI schema (drf-spectacular)
- [ ] Tests de API
- [ ] API documentada en /api/docs/

### 3c: Polish
- [ ] Type hints en serializers/viewsets
- [ ] Validaciones completas
- [ ] Filtrado funcionando
- [ ] Paginación configurada

---

## 📈 RESULTADO ESPERADO

### API Endpoints funcionales:

```
GET    /api/v1/organizations/          - Listar orgs
POST   /api/v1/organizations/          - Crear org
GET    /api/v1/organizations/{id}/     - Detalle
PATCH  /api/v1/organizations/{id}/     - Actualizar
DELETE /api/v1/organizations/{id}/     - Eliminar

GET    /api/v1/users/                  - Listar usuarios
POST   /api/v1/users/                  - Crear usuario
GET    /api/v1/users/{id}/             - Detalle
PATCH  /api/v1/users/{id}/             - Actualizar

GET    /api/v1/risks/                  - Listar riesgos
POST   /api/v1/risks/                  - Crear riesgo
GET    /api/v1/risks/{id}/             - Detalle
PATCH  /api/v1/risks/{id}/             - Actualizar

GET    /api/docs/                      - OpenAPI Swagger UI
GET    /api/schema/                    - OpenAPI schema JSON
```

---

## ⏱️ TIMELINE

**Día 1-2:** Tests (factories + unitarios)  
**Día 3-5:** DRF (serializers + viewsets + routing)  
**Día 6:** Polish (type hints + validaciones)  
**Día 7:** Final testing + documentation  

---

## 🚀 CÓMO COMENZAR

```bash
# 1. Leer este plan
# 2. Instalar drf-spectacular
pip install drf-spectacular

# 3. Comenzar con Paso 1 (Factories)
# 4. Ejecutar tests después de cada paso
pytest tests/ -v

# 5. Push a GitHub cuando cada etapa esté done
git add -A && git commit -m "feat: Fase 3a - Test improvements"
git push origin master
```

---

**Status:** 📋 PLAN LISTO  
**Próximo:** ¿Comenzamos con Paso 1 (Factories)?
