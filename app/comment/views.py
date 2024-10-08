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
from django.db.models import F
from django.shortcuts import get_object_or_404
from core.models import Post


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
    pagination_class = None

    def get_queryset(self):
        """Retrieve comments for the post."""
        queryset = self.queryset
        post_id = self.request.query_params.get('post')
        if post_id:
            post = get_object_or_404(Post, id=post_id)
            if not post.commentsEnabled:
                # No comments if comments are disabled
                return Comment.objects.none()
            queryset = queryset.filter(post=post)
            queryset = queryset.annotate(
                popularity=F('likeCount') + F('disLikeCount')
            ).order_by('-popularity', '-id')
        return queryset.distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        """Destroy a comment by its user"""
        if self.request.user == instance.user:
            instance.delete_comment(new_delete_status=1)
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
        post = serializer.validated_data['post']
        if not post.commentsEnabled:
            # Do not create comment if comments are disabled
            raise ValidationError("comments are disabled for this post!")
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
                {'detail': str(dict(e.detail))},
                status=status.HTTP_409_CONFLICT)

    def perform_create(self, serializer):
        """Create a new CommentReaction"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Destroy a comment by its user"""
        instance = self.get_object()
        if instance.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied(
                "You do not have permission to update this reaction.")
