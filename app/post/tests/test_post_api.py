
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from post.serializers import (
    PostSerializer,
    PostDetailSerializer
)

from core.models import (
    Post
)

import tempfile
import os
from PIL import Image

POST_URL = reverse("post:post-list")


def detail_url(post_id):
    """Create and return a recipe detail url."""
    return reverse('post:post-detail', args=[post_id])


def image_upload_url(post_id):
    """Create and return a recipe image url"""
    return reverse('post:post-upload-image', args=[post_id])

def create_category(user, **params):
    """Create postCategory and return it."""
    default = {
        'title': 'sample Category',
        'description': 'sample desc',
    }

def create_recipe(user, **params):
    """Create Recipe and return it."""
    defaults = {
        'title': 'Sample Recipe title',
        'time_minutes': 18,
        'price': Decimal('7.25'),
        'description': "Sample description of recipe.",
        'link': "http://example.com/recipe.pdf"
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)
