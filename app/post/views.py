from post import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    permissions,
    viewsets,
    # mixins,
    status
)
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import PostCategory
# from drf_spectacular.utils import (
#     extend_schema,
#     extend_schema_view,
#     OpenApiParameter,
#     OpenApiTypes
# )
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
class PostCategoryViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.PostCategoryDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostCategory.objects.all()

    def get_queryset(self):
        """Retrieve postCategories."""
        queryset = self.queryset
        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PostCategorySerializer
        elif self.action == 'upload_image':
            return serializers.PostCategoryImageSerializer

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
