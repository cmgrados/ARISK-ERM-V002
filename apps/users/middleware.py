from users.models import _thread_locals

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Asignar el organization_id al contexto del hilo actual
        if request.user.is_authenticated and hasattr(request.user, 'organization_id') and request.user.organization_id:
            _thread_locals.organization_id = request.user.organization_id
        else:
            _thread_locals.organization_id = None
            
        # 2. Procesar la vista
        response = self.get_response(request)
        
        # 3. Limpiar el hilo por seguridad (evita filtraciones en hilos reutilizados)
        _thread_locals.organization_id = None
        
        return response
