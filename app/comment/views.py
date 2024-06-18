from comment import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    permissions,
    viewsets,
    mixins,
    # status
)

from core.models import Comment, CommentReaction
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)


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
    serializer_class = serializers.CommentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_queryset(self):
        """Retrieve comments for the post."""
        post = self.request.query_params.get('post')
        queryset = self.queryset.filter(
            post__id=post
            )
        return queryset.distinct()

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
            queryset.filter(
                comment__id=comment
                )
        return queryset.distinct()

    def perform_create(self, serializer):
        """Create a new CommentReaction"""
        serializer.save(user=self.request.user)
