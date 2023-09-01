"""Test Recipe API"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipie
from recipe.serializers import  RecipeSerializer

RECIPE_URL =  reverse('recipe:recipe-list')
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 5,
        'price': Decimal('5.5'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf'

    }
    defaults.update(params)
    recipe = Recipie.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests,"""
    def setUp(self) -> None:
       self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)