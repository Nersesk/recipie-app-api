from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeiViewSet,
    TagViewSet)

router = DefaultRouter()
router.register('recipes', RecipeiViewSet)
router.register('tags', TagViewSet)
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
