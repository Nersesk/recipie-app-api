"""Test Recipe API"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipie,
    Tag
)

from recipe.serializers import (
    RecipeSerializer,
    RecipieDetailSerializer,
)

RECIPE_URL = reverse('recipe:recipie-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL"""
    return reverse('recipe:recipie-detail', args=(recipe_id,))


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


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated api requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email='user@examole.com', password ='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrive_recipies(self):
        """Test retrieving list of recipies"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipies = Recipie.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipie_list_limited_to_user(self):
        """Test limited recipies is limited to authenticated user."""
        other_user = create_user( email='other@examole.com', password='testpass12.3')
        create_recipe(other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipies = Recipie.objects.filter(user=self.user).order_by('-id')

        serializer = RecipeSerializer(recipies, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipie_detail(self):
        """Test get recipie detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipieDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_create_recipie(self):
        """Test creating a recipie"""
        payload = {
            'title': 'Sample recipe title',
            'time_minutes': 5,
            'price': Decimal('9.5')
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipie.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Testing partial update"""
        original_link="https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title="Sample recipie title",
            link=original_link
        )
        payload = {'title': "New recipe title"}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe"""
        recipe = create_recipe(
            user=self.user,
            title="Some title",
            link="https://example.com/recipe.pdf"
        )
        payload = {'title': "New recipe title",
                   'link': "https://example.com/recipe1.pdf",
                   'time_minutes': 10,
                   'price': Decimal('3.7')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the user results in an error."""
        new_user = create_user(email='user1@examole.com', password='testpass123')
        recipe = create_recipe(self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipie(self):
        """Test deleting recipe"""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipie.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete other users recipe"""
        new_user = create_user(email='user1@examole.com', password='testpass123')
        recipe = create_recipe(new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipie.objects.filter(id=recipe.id).exists())

    def test_create_recipie_with_new_tags(self):
        """Test creating recipie with new tag"""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipie.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipie_with_existing_tags(self):
        """Test creating recipie with existing test"""
        tag_indian = Tag.objects.create(user=self.user, name="Indian")

        payload =  {
            'title': "Pon",
            'time_minutes': 60,
            'price': Decimal(4.5),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipie.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipie"""
        recipie = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipie.id)

        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipie.tags.all())

    def test_update_recipie_assigning_tag(self):
        """Test assigning an existing tag when updating a recipie"""
        tag_breakfast = Tag.objects.create(user=self.user, name="Breakfast")
        recipie = create_recipe(user=self.user)
        recipie.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name="Lunch")
        payload = {'tags': [{'name': 'Lunch'}]}

        url = detail_url(recipie.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipie.tags.all())
        self.assertNotIn(tag_breakfast, recipie.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

