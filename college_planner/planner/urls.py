from django.urls import path
from . import views

app_name = 'planner'

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),
    path('research/<str:department>/', views.get_research_data, name='get_research_data'),
]