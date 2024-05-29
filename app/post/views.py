from post import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    permissions,
    viewsets,
    mixins,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import PostCategory, Post, Tag
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)
from django.utils import timezone


# @extend_schema_view(
#     list=extend_schema(
#         description=[
#             OpenApiParameter(
#                 'title',
#                 OpenApiTypes.STR,
#                 description='Name of category.',
#             ),
#             OpenApiParameter(
#                 'parentPostCategoryId',
#                 OpenApiTypes.INT,
#                 description='ID of parent category.',
#             ),
#             OpenApiParameter(
#                 'description',
#                 OpenApiTypes.STR,
#                 description='Optional',
#             ),
#             OpenApiParameter(
#                 'image',
#                 OpenApiTypes.STR,
#                 description='Optional',
#             )
#         ]
#     )
# )
class PostCategoryViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.PostCategoryDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostCategory.objects.all()

    def get_queryset(self):
        """Retrieve postCategories."""
        queryset = self.queryset
        return queryset.order_by('title').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostCategorySerializer
        # elif self.action == 'upload_image':
        #     return serializers.PostCategoryImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(
            createdBy=self.request.user,
            updatedBy=self.request.user,
            )

    def perform_update(self, serializer):
        serializer.save(
            updatedBy=self.request.user,
            updatedDate=timezone.now()
        )

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to postCategory."""
        postCategory = self.get_object()
        serializer = self.get_serializer(postCategory, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# from rest_framework.parsers import MultiPartParser, FormParser

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
        ]
    )
)
class PostViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.PostDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()

    # parser_classes = (MultiPartParser, FormParser)

    def get_allowed_methods(self):
        methods = super().get_allowed_methods()
        # Exclude DELETE method from the list of allowed methods
        if 'DELETE' in methods:
            methods.remove('DELETE')
        return methods

    def _params_to_ints(self, qs):
        """Convert list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def _params_to_strings(self, qs):
        """Convert list of strings to integers."""
        return qs.split(',')

    def get_queryset(self):
        """Retrieve recipe for authenticated user."""
        tags = self.request.query_params.get('tags')
        postCategoryId = self.request.query_params.get('postCategoryId')
        authorName = self.request.query_params.get('authorName')
        createdDate = self.request.query_params.get('createdDate')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if postCategoryId:
            postCategoryIds = self._params_to_ints(postCategoryId)
            queryset = queryset.filter(postCategoryId__in=postCategoryIds)
        if authorName:
            authorNames = self._params_to_strings(authorName)
            queryset = queryset.filter(authorName__in=authorNames)
        if createdDate:
            createdDate_rage = self._params_to_strings(createdDate)
            queryset = queryset.filter(createdDate__range=createdDate_rage)

        return queryset.all().order_by('-createdDate').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostSerializer
        # elif self.action == 'upload_image':
        #     return serializers.PostImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new post"""
        serializer.save(createdBy=self.request.user,
                        updatedBy=self.request.user,
                        updatedDate=timezone.now(),
                        createdDate=timezone.now())

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to post."""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to posts.',
            )
        ]
    )
)
class BasePostAttrViewSet(mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """Base viewset for post attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )  # default=0
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(post__isnull=False)

        return queryset.order_by('-name').distinct()


class TagViewSet(BasePostAttrViewSet):
    """Manage tags in the database"""
    # order of inputs is important
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
