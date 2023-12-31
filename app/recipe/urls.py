from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeiViewSet,
    TagViewSet,
    IngredientViewSet
)

router = DefaultRouter()
router.register('recipes', RecipeiViewSet)
router.register('tags', TagViewSet)
router.register('ingredient', IngredientViewSet)
app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
