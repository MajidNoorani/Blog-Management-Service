from comment import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    permissions,
    viewsets,
    mixins,
    status
)

from core.models import Comment, CommentReaction
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied


@extend_schema_view(
    list=extend_schema(
        description="""
        Retrieve all comments of post.
        """,
        parameters=[
            OpenApiParameter(
                'post',
                OpenApiTypes.INT,
                required=True
            ),
        ]
    )
)
class CommentViewSet(mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """View for manage comment APIs."""
    serializer_class = serializers.CommentDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_queryset(self):
        """Retrieve comments for the post."""
        queryset = self.queryset
        post = self.request.query_params.get('post')
        if post:
            queryset = self.queryset.filter(
                post__id=post
                )
        return queryset.distinct()

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return serializers.CommentSerializer
        return self.serializer_class

    def perform_destroy(self, instance):
        """Destroy a comment by its user"""
        instance = self.get_object()
        if instance.user == self.request.user:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied(
                "You do not have permission to delete this comment.")

    def perform_update(self, serializer):
        """Destroy a comment by its user"""
        instance = self.get_object()
        if instance.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied(
                "You do not have permission to update this comment.")

    def perform_create(self, serializer):
        """Create a new Comment"""
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """Allow unauthenticated access to GET requests."""
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return super().get_permissions()


@extend_schema_view(
    list=extend_schema(
        description="""
        Retrieve all reactions of the current user
        to all the comments of the specified post.
        """,
        parameters=[
            OpenApiParameter(
                'comment',
                OpenApiTypes.INT,
                required=True
            ),
        ]
    )
)
class CommentReactionViewSet(mixins.DestroyModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    """View for manage CommentReaction APIs."""

    serializer_class = serializers.CommentReactionSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = CommentReaction.objects.all()

    def get_queryset(self):
        """Retrieve comment reactions for authenticated user."""
        comment = self.request.query_params.get('comment')
        queryset = self.queryset.filter(user=self.request.user)
        if comment:
            queryset = queryset.filter(
                comment__id=comment
                )
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            )
        except ValidationError as e:
            return Response(
                {'detail': str(dict(e.detail)['non_field_errors'][0])},
                status=status.HTTP_409_CONFLICT)

    def perform_create(self, serializer):
        """Create a new CommentReaction"""
        serializer.save(user=self.request.user)
