from rest_framework import serializers
from core.models import PostCategory
# import re


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
        """Create postCategory"""
        # default values
        default_status = 'Inactive'
        postCategory = PostCategory.objects.create(
            status=default_status,
            **validated_data)

        return postCategory

    # def update(self, instance, validated_data):
    #     """Update postCategory"""
    #     validated_data['title'] = validated_data['title'].title()
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)

    #     instance.save()
    #     return instance


class PostCategoryDetailSerializer(PostCategorySerializer):
    """Serializer for postCategory detail view."""

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


class PostCategoryImageSerializer(serializers.ModelSerializer):
    """serializer for uploading image to postCategory."""

    class Meta:
        model = PostCategory
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
