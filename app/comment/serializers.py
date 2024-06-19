from rest_framework import serializers
from core.models import (
    Comment,
    CommentReaction
)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment Reactions"""

    currentUserReaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'comment', 'parentComment',
                  'likeCount', 'disLikeCount', 'currentUserReaction']
        read_only_fields = ['id', 'likeCount', 'disLikeCount']

    def get_currentUserReaction(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and obj:
            reaction = CommentReaction.objects.filter(
                user=user, comment=obj
                ).first()
            if reaction:
                return CommentReactionSerializer(reaction).data
        return None

    def create(self, validated_data):
        # tags excluded from validated data
        comment = Comment.objects.create(**validated_data)
        return comment

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CommentDetailSerializer(CommentSerializer):
    """Detail Serializer for Comment"""

    class Meta(CommentSerializer.Meta):
        pass


class CommentReactionSerializer(serializers.ModelSerializer):
    """Serializer for Comment Reactions"""

    class Meta:
        model = CommentReaction
        fields = ['id', 'reaction', 'comment']
        read_only_fields = ['id']

    def create(self, validated_data):
        # tags excluded from validated data
        commentReaction = CommentReaction.objects.create(**validated_data)
        return commentReaction

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
