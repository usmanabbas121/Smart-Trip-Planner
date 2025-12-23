from django.urls import path
from .views import CalculateTripView, HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('calculate-trip/', CalculateTripView.as_view(), name='calculate-trip'),
]

