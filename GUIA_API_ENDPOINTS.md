# 🚀 GUÍA DE ENDPOINTS API

**Fecha:** 2026-08-03  
**Versión API:** 1.0.0  
**Base URL:** `http://localhost:8000/api/v1/`

---

## 📋 Índice de Endpoints

### **Documentación Interactiva**
- Swagger UI: `http://localhost:8000/api/schema/swagger/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`
- OpenAPI JSON: `http://localhost:8000/api/schema/`

---

## 👥 USUARIOS & ORGANIZACIONES

### **Organizations**
```
GET    /api/v1/organizations/              # Listar organizaciones
POST   /api/v1/organizations/              # Crear (admin)
GET    /api/v1/organizations/{id}/         # Detalle
PUT    /api/v1/organizations/{id}/         # Actualizar (admin)
DELETE /api/v1/organizations/{id}/         # Eliminar (admin)
GET    /api/v1/organizations/{id}/users/   # Usuarios de la org
```

**Filtrado:**
```
GET /api/v1/organizations/?is_active=true
GET /api/v1/organizations/?search=acme
```

### **Users**
```
GET    /api/v1/users/                      # Listar usuarios
POST   /api/v1/users/                      # Crear usuario (admin)
GET    /api/v1/users/{id}/                 # Detalle usuario
PUT    /api/v1/users/{id}/                 # Actualizar (admin)
DELETE /api/v1/users/{id}/                 # Eliminar (admin)
GET    /api/v1/users/me/                   # Usuario actual
GET    /api/v1/users/{id}/permissions/    # Permisos usuario
POST   /api/v1/users/{id}/set_password/   # Cambiar contraseña (admin)
POST   /api/v1/users/{id}/activate/       # Activar usuario (admin)
POST   /api/v1/users/{id}/deactivate/     # Desactivar usuario (admin)
```

**Filtrado:**
```
GET /api/v1/users/?organization=1
GET /api/v1/users/?is_staff=true
GET /api/v1/users/?is_superuser=true
GET /api/v1/users/?is_risk_manager=true
GET /api/v1/users/?search=john
GET /api/v1/users/?ordering=-date_joined
```

### **Roles**
```
GET    /api/v1/roles/                      # Listar roles
POST   /api/v1/roles/                      # Crear rol (admin)
GET    /api/v1/roles/{id}/                 # Detalle rol
PUT    /api/v1/roles/{id}/                 # Actualizar rol (admin)
DELETE /api/v1/roles/{id}/                 # Eliminar rol (admin)
```

---

## ⚠️ RIESGOS

### **Risks**
```
GET    /api/v1/risks/                      # Listar riesgos
POST   /api/v1/risks/                      # Crear riesgo (admin)
GET    /api/v1/risks/{id}/                 # Detalle riesgo
PUT    /api/v1/risks/{id}/                 # Actualizar (admin)
DELETE /api/v1/risks/{id}/                 # Eliminar (admin)
GET    /api/v1/risks/{id}/causes/          # Causas del riesgo
GET    /api/v1/risks/{id}/consequences/    # Consecuencias
GET    /api/v1/risks/{id}/assessments/     # Evaluaciones
GET    /api/v1/risks/summary/              # Resumen estadísticas
```

**Filtrado:**
```
GET /api/v1/risks/?category=OPERATIONAL
GET /api/v1/risks/?criticality=HIGH
GET /api/v1/risks/?search=market risk
GET /api/v1/risks/?ordering=-criticality
```

### **Risk Causes**
```
GET    /api/v1/risk-causes/
POST   /api/v1/risk-causes/                # Crear (admin)
GET    /api/v1/risk-causes/{id}/
PUT    /api/v1/risk-causes/{id}/           # Actualizar (admin)
DELETE /api/v1/risk-causes/{id}/           # Eliminar (admin)
```

### **Risk Consequences**
```
GET    /api/v1/risk-consequences/
POST   /api/v1/risk-consequences/          # Crear (admin)
GET    /api/v1/risk-consequences/{id}/
PUT    /api/v1/risk-consequences/{id}/     # Actualizar (admin)
DELETE /api/v1/risk-consequences/{id}/     # Eliminar (admin)
```

### **Probability & Impact Scales (Read-Only)**
```
GET    /api/v1/probability-scales/         # Escala de probabilidad
GET    /api/v1/probability-scales/{id}/
GET    /api/v1/impact-scales/              # Escala de impacto
GET    /api/v1/impact-scales/{id}/
```

### **Risk Matrix Configuration**
```
GET    /api/v1/risk-matrix-configs/        # Matriz de riesgos (read-only)
GET    /api/v1/risk-matrix-configs/{id}/
```

### **Risk Assessments**
```
GET    /api/v1/risk-assessments/           # Listar evaluaciones
POST   /api/v1/risk-assessments/           # Crear (admin)
GET    /api/v1/risk-assessments/{id}/      # Detalle
PUT    /api/v1/risk-assessments/{id}/      # Actualizar (admin)
DELETE /api/v1/risk-assessments/{id}/      # Eliminar (admin)
```

**Filtrado:**
```
GET /api/v1/risk-assessments/?risk=1
GET /api/v1/risk-assessments/?inherent_severity=YELLOW
GET /api/v1/risk-assessments/?ordering=-residual_score
```

---

## 💰 CRÉDITO Y PORTFOLIO

### **Customers**
```
GET    /api/v1/customers/                  # Listar clientes
POST   /api/v1/customers/                  # Crear cliente (admin)
GET    /api/v1/customers/{id}/             # Detalle cliente
PUT    /api/v1/customers/{id}/             # Actualizar (admin)
DELETE /api/v1/customers/{id}/             # Eliminar (admin)
GET    /api/v1/customers/{id}/operations/           # Operaciones cliente
GET    /api/v1/customers/{id}/portfolio_summary/    # Resumen portfolio
```

**Filtrado:**
```
GET /api/v1/customers/?search=john
GET /api/v1/customers/?segment=MICROENTERPRISE
GET /api/v1/customers/?economic_activity=retail
```

### **Credit Operations**
```
GET    /api/v1/credit-operations/                  # Listar operaciones
POST   /api/v1/credit-operations/                  # Crear (admin)
GET    /api/v1/credit-operations/{id}/             # Detalle
PUT    /api/v1/credit-operations/{id}/             # Actualizar (admin)
DELETE /api/v1/credit-operations/{id}/             # Eliminar (admin)
GET    /api/v1/credit-operations/{id}/metrics/     # Métricas de riesgo
GET    /api/v1/credit-operations/summary/          # Resumen portfolio
GET    /api/v1/credit-operations/high_risk/        # Créditos de alto riesgo (>90 días)
GET    /api/v1/credit-operations/critical/         # Créditos críticos (>180 días)
GET    /api/v1/credit-operations/by_currency/      # Agrupado por moneda
```

**Filtrado:**
```
GET /api/v1/credit-operations/?customer=1
GET /api/v1/credit-operations/?currency=PEN
GET /api/v1/credit-operations/?agency=Lima
GET /api/v1/credit-operations/?credit_type=CONSUMO
GET /api/v1/credit-operations/?load_date=2026-08-01
GET /api/v1/credit-operations/?ordering=-days_past_due
```

### **Credit Risk Metrics**
```
GET    /api/v1/credit-risk-metrics/       # Listar métricas
POST   /api/v1/credit-risk-metrics/       # Crear (admin)
GET    /api/v1/credit-risk-metrics/{id}/  # Detalle
PUT    /api/v1/credit-risk-metrics/{id}/  # Actualizar (admin)
DELETE /api/v1/credit-risk-metrics/{id}/  # Eliminar (admin)
```

### **Credit Risk Parameters**
```
GET    /api/v1/credit-risk-parameters/            # Listar parámetros
POST   /api/v1/credit-risk-parameters/            # Crear (admin)
GET    /api/v1/credit-risk-parameters/{id}/       # Detalle
PUT    /api/v1/credit-risk-parameters/{id}/       # Actualizar (admin)
DELETE /api/v1/credit-risk-parameters/{id}/       # Eliminar (admin)
```

---

## 📝 Ejemplos de Solicitudes

### **Crear Usuario (Admin)**
```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "organization": 1,
    "is_risk_manager": true
  }'
```

### **Crear Riesgo (Admin)**
```bash
curl -X POST http://localhost:8000/api/v1/risks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Market Risk",
    "description": "Risk from market volatility",
    "category": "OPERATIONAL",
    "criticality": "HIGH",
    "owner": 1
  }'
```

### **Crear Operación de Crédito (Admin)**
```bash
curl -X POST http://localhost:8000/api/v1/credit-operations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "customer": 1,
    "operation_code": "OP-000123",
    "product_name": "Personal Loan",
    "disbursement_date": "2026-01-01",
    "original_amount": "50000.00",
    "currency": "PEN",
    "balance": "45000.00",
    "rate": "12.50",
    "term": 60
  }'
```

### **Listar Riesgos Críticos**
```bash
curl http://localhost:8000/api/v1/risks/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Respuesta:
```json
{
  "total_risks": 15,
  "by_category": {
    "OPERATIONAL": 5,
    "TECHNOLOGICAL": 3,
    "LEGAL": 7
  },
  "by_criticality": {
    "LOW": 2,
    "MEDIUM": 8,
    "HIGH": 4,
    "CRITICAL": 1
  },
  "high_risk_count": 5
}
```

### **Listar Créditos de Alto Riesgo**
```bash
curl http://localhost:8000/api/v1/credit-operations/high_risk/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Resumen Portfolio Cliente**
```bash
curl http://localhost:8000/api/v1/customers/1/portfolio_summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Respuesta:
```json
{
  "customer_id": 1,
  "customer_name": "John Doe",
  "total_operations": 5,
  "total_current_portfolio": "250000.00",
  "total_past_due_portfolio": "15000.00",
  "total_provisions": "5000.00",
  "high_risk_operations": 2,
  "critical_operations": 0
}
```

---

## 🔐 Autenticación

### **Session Authentication**
```bash
# 1. Login en /admin/
curl -X POST http://localhost:8000/admin/login/

# 2. Usar la sesión en requests
curl http://localhost:8000/api/v1/users/ \
  -b "sessionid=YOUR_SESSION_ID"
```

### **Custom Token (Future)**
Próximamente: implementar TokenAuthentication para mobile apps

---

## 📊 Paginación

Todos los endpoints de list devuelven:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/risks/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parámetros:**
```
?page=2                    # Página específica
?page_size=50             # Items por página (default 20)
```

---

## 🔍 Búsqueda y Ordenamiento

**Búsqueda (SearchFilter):**
```
GET /api/v1/users/?search=john
GET /api/v1/risks/?search=market
GET /api/v1/customers/?search=12345678
```

**Ordenamiento (OrderingFilter):**
```
GET /api/v1/users/?ordering=username
GET /api/v1/users/?ordering=-date_joined         # Descendente
GET /api/v1/risks/?ordering=-criticality,name
```

---

## ✅ Status Codes

- `200 OK` - Solicitud exitosa
- `201 Created` - Recurso creado
- `204 No Content` - Eliminado exitosamente
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permiso
- `404 Not Found` - Recurso no existe
- `500 Server Error` - Error del servidor

---

## 🐛 Debugging

### **Ver request/response completo:**
```bash
curl -v http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Con pretty-print JSON:**
```bash
curl http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" | python -m json.tool
```

---

## 📚 Herramientas Recomendadas

- **Postman** - GUI para testing de APIs
- **Insomnia** - Alternative to Postman
- **curl** - Command line HTTP client
- **httpie** - curl más amigable
- **Django REST Framework Browsable API** - En el navegador

---

**Generado:** 2026-08-03  
**Status:** API Ready ✅
