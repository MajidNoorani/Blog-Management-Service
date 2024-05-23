from rest_framework import serializers
from core.models import PostCategory


class PostCategorySerializer(serializers.ModelSerializer):
    """Serializer for postCategory"""

    parentPostCategoryId = serializers.PrimaryKeyRelatedField(
        queryset=PostCategory.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = PostCategory
        fields = ['id', 'title', 'parentPostCategoryId', 'description']
        read_only_fields = ['id']

        def create(self, validated_data):
            # default values
            default_status = 'Inactive'

            auth_user = self.context['request'].user
            postCategory = PostCategory.objects.create(
                createdBy=auth_user,
                updatedBy=auth_user,
                status=default_status,
                **validated_data)

            return postCategory

        def update(self, instance, validated_data):
            """Update postCategory"""
            auth_user = self.context['request'].user

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            setattr(instance, 'updatedBy', auth_user)
            instance.save()
            return instance


class PostCategoryDetailSerializer(PostCategorySerializer):
    """Serializer for recipe detail view."""

    class Meta(PostCategorySerializer.Meta):
        fields = PostCategorySerializer.Meta.fields + [
            'description',
            'createdBy',
            'createdDate',
            'updatedBy',
            'updatedDate'
            ]
        read_only_fields = PostCategorySerializer.Meta.read_only_fields + [
            'createdBy', 'createdDate', 'updatedBy', 'updatedDate'
        ]


class RecipeImageSerializer(serializers.ModelSerializer):
    """serializer for uploading image to postCategory."""

    class Meta:
        model = PostCategory
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
