"""
Test custom user model
"""

from django.contrib.auth import get_user_model
from django.test import TestCase


class TestModel(TestCase):
    """Tests for Models"""

    def test_user_creation_with_email(self):
        """
        Test creating user with email Success
        """
        email = "test@example.com"
        password = "Test10201."
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test@examplE.com', 'test@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['test3@Example.Com', 'test3@example.com']
        ]
        for email, excepted in sample_emails:
            user = get_user_model().objects.create_user(email, "sometest1")
            self.assertEqual(user.email, excepted)

    def test_new_user_without_email_raises_error(self):
        """Testing error when email not provided"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', "somepasswrd")

    def test_create_super_user(self):
        """Testing superuser creating success"""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "sometestpass1"
        )

        self.assertTrue(user.is_superuser)