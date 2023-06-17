from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import   ConnectionViewSet

app_name = 'connections'

router = DefaultRouter()
router.register('', ConnectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
