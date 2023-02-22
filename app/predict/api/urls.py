from django.urls import path, include
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from predict.api.views import PredictViewSet


router = DefaultRouter()
router.register('', PredictViewSet)

app_name = 'predict'

urlpatterns = [
    path('', include(router.urls)),
]
