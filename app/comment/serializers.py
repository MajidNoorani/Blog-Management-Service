from rest_framework import serializers
from core.models import (
    Comment,
    CommentReaction,
    User
)


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment Reactions"""

    currentUserReaction = serializers.SerializerMethodField()
    createdByCurrentUser = serializers.SerializerMethodField()
    user = CommentUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'comment', 'parentComment',
                  'likeCount', 'disLikeCount', 'createdByCurrentUser',
                  'currentUserReaction', 'user']
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

    def get_createdByCurrentUser(self, obj):
        user = self.context['request'].user
        if user.is_authenticated and obj:
            return obj.user == user
        return False

    def create(self, validated_data):
        # tags excluded from validated data
        comment = Comment.objects.create(**validated_data)
        return comment

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CommentReactionSerializer(serializers.ModelSerializer):
    """Serializer for Comment Reactions"""

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        comment = data.get('comment')

        # Check if we are updating an instance
        instance = self.instance

        if instance is None:
            # Only check for uniqueness on creation
            if CommentReaction.objects.filter(user=user,
                                              comment=comment
                                              ).exists():
                raise serializers.ValidationError(
                    "Current user has already put a reaction on this comment.")

        return data

    class Meta:
        model = CommentReaction
        fields = ['id', 'reaction', 'comment']
        read_only_fields = ['id']

    def create(self, validated_data):
        commentReaction = CommentReaction.objects.create(
            **validated_data)
        return commentReaction

    def update(self, instance, validated_data):
        if instance.user != self.context['request'].user:
            raise serializers.ValidationError(
                "You do not have permission to edit this comment reaction.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
