import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.FILES:
            logger.info(f"Arquivos recebidos: {request.FILES}")
            for name, file in request.FILES.items():
                logger.info(f"Arquivo {name}: {file.name} ({file.size} bytes)")
        
        return response