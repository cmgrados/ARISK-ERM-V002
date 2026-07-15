import json
from .models import ActivityLog

class ActivityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Log only authenticated users and modifying actions (POST, PUT, DELETE)
        # to avoid database bloat from GET requests.
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE']:
            # Ignore some internal or repetitive paths if needed, but for now we log all.
            ip = request.META.get('REMOTE_ADDR')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            
            description = f"Método: {request.method}"
            if request.method == 'POST':
                description = "Modificación/Creación de registros (POST)"
            elif request.method == 'DELETE':
                description = "Eliminación de registros (DELETE)"
                
            ActivityLog.objects.create(
                user=request.user,
                action=request.method,
                path=request.path,
                description=description,
                ip_address=ip
            )
            
        return response
