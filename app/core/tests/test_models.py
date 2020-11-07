from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core import models


def sample_user(email='tester01@londonapp.com', password='tester01_pass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        """Test creating a new user with an email is successfull"""
        email = 'test@email.com'
        password = 'TestPassword123'
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@LONDONAPPDEV.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_blank_email(self):
        """Test user created with no email yields an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "1234")

    def test_new_user_invalid_email(self):
        """Test user created with invalid email yields an error"""
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user("   ", "1234")

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        email = "master@email.com"
        user = "masterOfMasters"
        user = get_user_model().objects.create_superuser(email, user)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)
