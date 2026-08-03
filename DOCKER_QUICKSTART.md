# 🐳 ARISK ERM - Docker Quick Start Guide

## Prerequisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- 4GB RAM mínimo
- 10GB espacio en disco

### Instalar Docker

**Windows:**
```
Descargar: https://www.docker.com/products/docker-desktop
Instalar Docker Desktop
```

**Mac:**
```
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

---

## 🚀 Quick Start (5 minutos)

### 1. Clonar Repositorio

```bash
git clone https://github.com/cmgrados/ARISK-ERM-V002.git
cd ARISK-ERM-V002
```

### 2. Crear Archivo .env

```bash
cp .env.local .env
```

**Opcionalmente, editar .env para producción:**
```bash
# Cambiar estas variables:
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<nueva-clave-segura>
ALLOWED_HOSTS=tu-dominio.com
DB_PASSWORD=<nueva-contraseña-fuerte>
```

### 3. Build y Start Docker

```bash
# Primera vez (construye imagen)
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web
```

### 4. Crear Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Acceder a la Aplicación

- **Web**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Health**: http://localhost:8000/health

---

## 📊 Servicios en Ejecución

| Servicio | Puerto | URL | Propósito |
|----------|--------|-----|-----------|
| Django | 8000 | http://localhost:8000 | Aplicación web |
| PostgreSQL | 5432 | localhost:5432 | Base de datos |
| Redis | 6379 | localhost:6379 | Cache |
| Nginx | 80, 443 | http://localhost | Reverse proxy |

---

## 🛠️ Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado de servicios
docker-compose ps

# Detener servicios
docker-compose stop

# Reiniciar servicios
docker-compose restart

# Eliminar contenedores (pero mantiene datos en volúmenes)
docker-compose down

# Eliminar TODO (datos, volúmenes, imágenes locales)
docker-compose down -v
```

### Base de Datos

```bash
# Ver logs de PostgreSQL
docker-compose logs db

# Ejecutar comando en postgres
docker-compose exec db psql -U arisk -d arisk_erm

# Backup de base de datos
docker-compose exec db pg_dump -U arisk arisk_erm > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U arisk arisk_erm < backup.sql
```

### Django Management

```bash
# Migraciones
docker-compose exec web python manage.py migrate

# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Shell Django
docker-compose exec web python manage.py shell

# Ejecutar tests
docker-compose exec web pytest tests/
```

### Logs

```bash
# Todos los logs
docker-compose logs

# Logs de un servicio específico
docker-compose logs web
docker-compose logs db
docker-compose logs nginx

# Seguimiento en vivo
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100
```

---

## 🔍 Troubleshooting

### Error: "Address already in use"

El puerto está siendo usado por otro proceso.

```bash
# Windows - encontrar proceso usando puerto 8000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Matar el proceso (Windows)
taskkill /PID <PID> /F

# Matar el proceso (Linux/Mac)
kill -9 <PID>
```

### Error: "Database connection refused"

PostgreSQL no está listo.

```bash
# Ver logs de BD
docker-compose logs db

# Esperar a que esté listo (suele tomar 10-20 segundos)
docker-compose ps
```

### Error: "Connection refused" en Nginx

Django no está respondiendo.

```bash
# Ver logs de Django
docker-compose logs web

# Reiniciar Django
docker-compose restart web
```

### Limpiar volúmenes y empezar de nuevo

```bash
# ADVERTENCIA: Esto elimina TODOS los datos
docker-compose down -v
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py createsuperuser
```

---

## 📝 Notas Importantes

### Desarrollo vs Producción

**Desarrollo (.env.local):**
- DEBUG=True
- SQLite o PostgreSQL (flexible)
- Email en consola

**Producción (.env):**
- DEBUG=False
- PostgreSQL REQUIERIDO
- SSL/HTTPS habilitado
- Email SMTP real

### Persistencia de Datos

Los datos se guardan en Docker Volumes:
- `postgres_data` - Base de datos PostgreSQL
- `redis_data` - Cache Redis
- `static_volume` - Archivos estáticos
- `media_volume` - Archivos de usuario

Para ver volúmenes:
```bash
docker volume ls
docker volume inspect arisk-erm_postgres_data
```

### Performance

Para mejorar performance:
```bash
# En docker-compose.yml, aumentar workers:
# --workers 8  (si tienes 4+ cores)

# En nginx.conf, aumentar conexiones:
# worker_connections 2048;

# En Redis, habilitar persistencia:
# appendonly yes
```

---

## 🚀 Deployment Rápido

### AWS EC2

```bash
# 1. Crear instancia EC2 (Ubuntu 22.04, t3.medium)
# 2. Conectar vía SSH
# 3. Ejecutar:

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

git clone https://github.com/cmgrados/ARISK-ERM-V002.git
cd ARISK-ERM-V002
cp .env.example .env
# Editar .env con valores de producción
docker-compose -f docker-compose.yml up -d
```

### Heroku

```bash
# 1. Instalar Heroku CLI
# 2. heroku login
# 3. heroku create your-app-name
# 4. heroku addons:create heroku-postgresql:standard-0
# 5. git push heroku main
```

### DigitalOcean App Platform

```bash
# 1. Conectar repositorio GitHub
# 2. Crear app desde Dockerfile
# 3. Configurar variables de entorno
# 4. Deploy automático
```

---

## 📚 Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Nginx Docker](https://hub.docker.com/_/nginx)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)

---

**Status:** ✅ Production Ready

Generado: 2026-08-03
