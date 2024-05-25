"""
Tests for recipe APIs.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from post.serializers import (
    PostCategorySerializer,
    PostCategoryDetailSerializer
)

from core.models import (
    PostCategory
)

import tempfile
import os
from PIL import Image


POSTCATEGORY_URL = reverse("post:postcategory-list")


def detail_url(postCategory_id):
    """Create and return a postCategory detail url."""
    return reverse('post:postcategory-detail', args=[postCategory_id])


def image_upload_url(postCategory_id):
    """Create and return a recipe image url"""
    return reverse('post:postcategory-upload-image', args=[postCategory_id])


def create_postCategory(user, **params):
    """Create postCategory and return it."""
    defaults = {
        'title': 'Main Category Title',
        'description': "Sample description of postCategory.",
        'parentPostCategoryId': None
    }
    defaults.update(params)

    postCategory = PostCategory.objects.create(createdBy=user,
                                               updatedBy=user,
                                               **defaults)
    return postCategory


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicPostCategoryAPITests(TestCase):
    """Test Unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Tests auth is required to call API."""

        res = self.client.get(POSTCATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            name='Test User',
            email='test@example.com',
            password='testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_postCategories(self):
        """Tests retrieving a list of recipes"""

        create_postCategory(user=self.user)
        create_postCategory(user=self.user, title='Main Category 2 Title')

        res = self.client.get(POSTCATEGORY_URL)

        recipes = PostCategory.objects.all().order_by('-id')
        serializer = PostCategorySerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_postCategories_detail(self):
        """Tests get recipe detail."""
        postCategories = create_postCategory(user=self.user)

        url = detail_url(postCategories.id)
        res = self.client.get(url)

        serializer = PostCategoryDetailSerializer(postCategories)
        self.assertEqual(serializer.data, res.data)

    # def test_create_postCategory_with_parent(self):
    #     """Test creating a postCategory."""
    #     main_category = create_postCategory(
    #         user=self.user,
    #         title='Main Category 2 Title'
    #         )
    #     payload = {
    #         'title': 'Sample Title',
    #         'description': 'Sample Desc',
    #         'parentPostCategoryId': main_category.id
    #     }

    #     res = self.client.post(POSTCATEGORY_URL, payload)

    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     postCategory = PostCategory.objects.get(id=res.data['id'])

    #     self.assertEqual(payload['title'], postCategory.title)
    #     self.assertEqual(payload['description'], postCategory.description)
    #     print(main_category.title)
    #     self.assertEqual(main_category.title, postCategory.parentPostCategoryId)
    #     self.assertEqual(self.user, postCategory.createdBy)
    #     self.assertEqual(self.user, postCategory.updatedBy)

