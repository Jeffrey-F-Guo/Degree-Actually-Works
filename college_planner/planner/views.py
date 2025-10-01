from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services.data_processor import DataProcessor
from .services.microservice_client import MicroserviceClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Create your views here.
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Django + microservice.
    
    GET /api/health/
    """
    try:
        client = MicroserviceClient()
        microservice_healthy = client.test_connection()
        
        return JsonResponse({
            'django_status': 'healthy',
            'microservice_status': 'healthy' if microservice_healthy else 'unhealthy',
            'overall_status': 'healthy' if microservice_healthy else 'degraded'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JsonResponse({
            'django_status': 'unhealthy',
            'microservice_status': 'error',
            'overall_status': 'degraded',
            'error': str(e)
        }, status=503)

@require_http_methods(["GET"])
def get_research_data(request, department):
    """
    Get research data for a given department.
    
    GET /api/research/
    """
    try:
        client = MicroserviceClient()
        research_data = client.get_research(department)
        return JsonResponse({
            'status': 'success',
            'department': department,
            'count': len(research_data),
            'data': research_data
        })
        
    except Exception as e:
        logger.error(f"Error getting research data for {department}: {e}")
        return JsonResponse({
            'status': 'error',
            'department': department,
            'error': str(e)
        }, status=500)
    
@require_http_methods(["GET"])
def get_course_data(request, department):
    """
    Get course data for a given department.
    
    GET /api/course/
    """

    try:
        client = MicroserviceClient()
        course_data = client.get_course(department)
        return JsonResponse({
            'status': 'success',
            'department': department,
            'count': len(course_data),
            'data': course_data
        })

    except Exception as e:
        logger.error(f"Error getting course data for {department}")
        return JsonResponse({
            'status': 'error',
            'department': department,
            'error': e
        })