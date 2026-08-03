# 🚀 ARISK ERM - DEPLOYMENT GUIDE

**Fase 4: Production Deployment**

---

## 📋 Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Setup Local con Docker](#setup-local-con-docker)
3. [Deployment en Producción](#deployment-en-producción)
4. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
5. [Troubleshooting](#troubleshooting)

---

## Requisitos

### **Para Development**
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- 4GB RAM mínimo
- 10GB disco disponible

### **Para Production**
- VPS/Cloud instance (AWS EC2, Digital Ocean, Heroku, etc.)
- Domain name
- SSL certificate (Let's Encrypt recomendado)
- PostgreSQL 14+ (o usar hosted database)
- Redis 7+ (opcional pero recomendado)
- Nginx reverse proxy

---

## Setup Local con Docker

### **1. Clonar Repositorio**

```bash
git clone https://github.com/cmgrados/ARISK-ERM-V002.git
cd ARISK-ERM-V002
```

### **2. Configurar Variables de Entorno**

```bash
# Copiar template
cp .env.example .env

# Editar .env con valores locales
# Mínimo necesario:
# - SECRET_KEY
# - DATABASE_URL
# - DEBUG=True (para dev)
```

### **3. Iniciar Contenedores**

```bash
# Build images (primera vez)
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web
```

### **4. Ejecutar Migraciones**

```bash
# Dentro del contenedor
docker-compose exec web python manage.py migrate

# O desde afuera
docker-compose exec web python manage.py migrate
```

### **5. Crear Superuser**

```bash
docker-compose exec web python manage.py createsuperuser
```

### **6. Ver Aplicación**

```
Web:      http://localhost:8000
Admin:    http://localhost:8000/admin
API:      http://localhost:8000/api/v1/
Swagger:  http://localhost:8000/api/schema/swagger/
Nginx:    http://localhost (puerto 80)
```

---

## Deployment en Producción

### **Opción A: VPS (AWS EC2, DigitalOcean, Linode)**

#### **Paso 1: Provisionar VPS**

```bash
# Ejemplo: DigitalOcean Ubuntu 22.04
# - 2GB RAM
# - 50GB SSD
# - $12/mes
```

#### **Paso 2: Instalar Docker**

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario actual a grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

#### **Paso 3: Clonar y Configurar**

```bash
# Clonar repositorio
git clone https://github.com/cmgrados/ARISK-ERM-V002.git
cd ARISK-ERM-V002

# Crear .env con valores de producción
cp .env.example .env
nano .env  # Editar valores

# Valores importantes para producción:
# ENVIRONMENT=production
# DEBUG=False
# SECRET_KEY=<new-secure-key>
# ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# DATABASE_URL=postgresql://user:password@db-host:5432/dbname
# SECURE_SSL_REDIRECT=True
```

#### **Paso 4: Setup PostgreSQL (Opción Cloud)**

**Recomendado:** Usar managed database (AWS RDS, DigitalOcean DBaaS)

```bash
# O instalar localmente
docker run -d \
  --name postgres-arisk \
  -e POSTGRES_DB=arisk_erm \
  -e POSTGRES_USER=arisk \
  -e POSTGRES_PASSWORD=<secure-password> \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine
```

#### **Paso 5: Setup SSL con Let's Encrypt**

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot certonly --standalone -d your-domain.com

# Crear directorio SSL en proyecto
mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*

# Auto-renewal
sudo certbot renew --dry-run
```

#### **Paso 6: Iniciar Aplicación**

```bash
# Construir
docker-compose -f docker-compose.yml build

# Iniciar (detached)
docker-compose -f docker-compose.yml up -d

# Verificar
docker-compose ps
docker-compose logs web
```

#### **Paso 7: Configurar Firewall**

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### **Opción B: Heroku Deployment**

```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Crear app
heroku create your-app-name

# 4. Agregar PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# 5. Agregar Redis
heroku addons:create heroku-redis:premium-0

# 6. Configurar variables
heroku config:set \
  ENVIRONMENT=production \
  SECRET_KEY=<key> \
  DEBUG=False \
  ALLOWED_HOSTS=your-app-name.herokuapp.com

# 7. Deploy
git push heroku main

# 8. Migraciones
heroku run python manage.py migrate

# 9. Crear superuser
heroku run python manage.py createsuperuser
```

### **Opción C: AWS ECS (Elastic Container Service)**

```bash
# 1. Push imagen a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker tag arisk-erm:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/arisk-erm:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/arisk-erm:latest

# 2. Crear ECS task definition
# 3. Crear ECS service
# 4. Setup RDS database
# 5. Setup ALB (load balancer)
```

---

## Monitoreo y Mantenimiento

### **Health Checks**

```bash
# Endpoint de salud
curl http://localhost:8000/health

# Nginx health
curl -I http://localhost/health

# Redis health
docker-compose exec redis redis-cli ping
```

### **Logs**

```bash
# Web app logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# Nginx logs
docker-compose logs -f nginx

# Ver últimas 100 líneas
docker-compose logs --tail=100 web
```

### **Backups**

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U arisk arisk_erm > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U arisk arisk_erm < backup.sql

# Backup volúmenes
docker run --rm -v arisk-erm_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz -C /data .
```

### **Actualizaciones**

```bash
# Pull últimas changes
git pull origin main

# Rebuild imagen
docker-compose build

# Reiniciar servicios
docker-compose up -d

# Ejecutar migraciones si es necesario
docker-compose exec web python manage.py migrate

# Recolectar static files
docker-compose exec web python manage.py collectstatic --noinput
```

---

## Troubleshooting

### **Aplicación no inicia**

```bash
# Ver logs detallados
docker-compose logs web

# Verificar configuración
docker-compose exec web python manage.py check

# Verificar database
docker-compose exec web python manage.py dbshell
```

### **Database connection error**

```bash
# Verificar conexión
docker-compose exec web python -c "import psycopg2; psycopg2.connect('...')"

# Ver logs de database
docker-compose logs db

# Verificar variables de entorno
docker-compose exec web env | grep DATABASE
```

### **Static files not loading**

```bash
# Recolectar static files
docker-compose exec web python manage.py collectstatic --clear --noinput

# Verificar volumen
docker-compose exec nginx ls -la /app/staticfiles/
```

### **Memory issues**

```bash
# Aumentar workers de gunicorn en docker-compose.yml
# Cambiar: --workers 4
# A: --workers 2

# O aumentar RAM de contenedor
# En docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

### **SSL certificate issues**

```bash
# Verificar certificado
openssl x509 -in ssl/cert.pem -text -noout

# Renovar certificado
sudo certbot renew --force-renewal

# Copiar nuevamente
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

---

## Performance Optimization

### **Nginx Caching**

```nginx
# En nginx.conf
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### **Database Optimization**

```sql
-- Crear índices
CREATE INDEX idx_credit_operation_customer ON credit_operation(customer_id);
CREATE INDEX idx_credit_operation_days_past_due ON credit_operation(days_past_due);

-- Analizar tablas
ANALYZE;
```

### **Redis Caching**

```python
# En settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}
```

---

## Monitoreo Avanzado (Opcional)

### **Sentry (Error Tracking)**

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1
)
```

### **Prometheus + Grafana**

```yaml
# docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

---

## Checklist de Deployment

- [ ] SECRET_KEY generada y segura
- [ ] DEBUG=False en producción
- [ ] Database URL configurada
- [ ] SSL certificado instalado
- [ ] ALLOWED_HOSTS actualizado
- [ ] Migraciones ejecutadas
- [ ] Superuser creado
- [ ] Static files recolectados
- [ ] Firewall configurado
- [ ] Backups automatizados
- [ ] Monitoring/alerting activo
- [ ] DNS apuntando a servidor
- [ ] Health checks pasando
- [ ] API documentación accesible
- [ ] Logs centralizados

---

## Próximos Pasos

1. **Monitoreo:** Configurar Sentry/Prometheus
2. **Backups:** Automatizar backups diarios
3. **CI/CD:** Configurar auto-deploy en push
4. **Scaling:** Configurar auto-scaling si es necesario
5. **Analytics:** Agregar tracking de eventos

---

**Status:** ✅ Deployment Ready

Generado: 2026-08-03
