# create temporary files
import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from core.models import Recipe, Tag, Ingredient


RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_user(email='tester01@londonapp.com', password='tester01_pass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_tag(user, name='Main course'):
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='cinamon'):
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """Create a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that the authentication is required"""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test autenticated recipe api """

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """test retrieve a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        user2 = sample_user('other@app.dev.comm', 'password123')
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test for recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Create a basic recipe"""
        payload = {
            'title': 'Chocolate cheescake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='grapes')
        ingredient2 = sample_ingredient(user=self.user, name='strawberries')
        payload = {
            'title': 'Strawberry grape cake',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka',
                   'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@londonappdev.com'
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def upload_image(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            # save an image to file
            img = Image.new('RGB', (32, 32))
            img.save(ntf, format='JPEG')
            # go back to the beginning of the file
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.state, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def upload_invalid_image(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
