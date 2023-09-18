"""Test for Ingredients API."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


def get_ingredient_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=(ingredient_id,))


class PublicIngredientsTest(TestCase):
    """Test unauthenticated API requests,"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """The auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsTest(TestCase):
    """Test authenticated api requests"""

    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_list_of_ingredients(self):
        Ingredient.objects.create(name='first', user=self.user)
        Ingredient.objects.create(name='second', user=self.user)

        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        Ingredient.objects.create(name='first', user=self.user)
        Ingredient.objects.create(name='second', user=self.user)

        user_1 = create_user(email="some_email@example.com")
        Ingredient.objects.create(name='third', user=user_1)
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_update_ingredients(self):
        ingredient = Ingredient.objects.create(name='first', user=self.user)
        url = get_ingredient_url(ingredient.id)
        payload = {
            'name': 'second',
        }

        res = self.client.patch(url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(ingredient.name, payload['name'])