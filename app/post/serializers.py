from rest_framework import serializers
from core.models import (
    PostCategory,
    Post,
    Tag,
    SEOKeywords
)


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
            'image',
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


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag"""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SEOKeywordsSerializer(serializers.ModelSerializer):
    """Serializer for seo keywords"""

    class Meta:
        model = SEOKeywords
        fields = ['id', 'keyword']
        read_only_fields = ['id']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for post"""
    tags = TagSerializer(many=True, required=False)

    relatedPosts = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        allow_null=True,
        required=False,
        many=True
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'postCategoryId', 'content', 'tags',
                  'postStatus', 'reviewStatus', 'isExternalSource',
                  'externalLink', 'excerpt', 'authorName',
                  'metaDescription', 'readTime', 'relatedPosts',
                  'image', 'updatedDate']
        read_only_fields = ['id', 'reviewStatus']
        extra_kwargs = {'image': {'required': True}}

    def _get_or_create_tags(self, tags, post):
        """Handle getting or creating tags as needed."""
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                **tag,
                defaults={'createdBy': self.context['request'].user,
                          'updatedBy': self.context['request'].user}
            )
            post.tags.add(tag_obj)

    def _get_related_post(self, relatedPosts, post):
        """Handle getting posts as needed."""
        for relatedPost in relatedPosts:
            related_post_obj = Post.objects.get(pk=relatedPost.id)
            post.relatedPosts.add(related_post_obj)

    def create(self, validated_data):
        # tags and relatedPosts excluded from validated data
        tags = validated_data.pop('tags', [])
        relatedPosts = validated_data.pop('relatedPosts', [])
        # content_data = validated_data.pop('content')
        # by default the status of the post is draft
        validated_data['postStatus'] = 'draft'
        # validated_data['content'] = content_data

        post = Post.objects.create(
            **validated_data)
        # post.content = CustomJsonField(**content_data)
        self._get_or_create_tags(tags, post)
        self._get_related_post(relatedPosts, post)

        return post

    def update(self, instance, validated_data):
        """Update recipe"""
        tags = validated_data.pop('tags', None)
        relatedPosts = validated_data.pop('relatedPosts', None)

        if tags is not None:
            # empty list is not None
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if relatedPosts is not None:
            # empty list is not None
            instance.relatedPosts.clear()
            self._get_related_post(relatedPosts, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PostDetailSerializer(PostSerializer):
    """Serializer for postCategory detail view."""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            'postPublishDate',
            'commentsEnabled',
            'seoKeywords',
            'createdBy',
            'createdDate',
            'updatedBy',
            'reviewResponseDate'
            ]
        read_only_fields = PostSerializer.Meta.read_only_fields + [
            'createdBy', 'createdDate', 'updatedBy', 'updatedDate',
            'postPublishDate', 'commentsEnabled', 'seoKeywords',
            'reviewResponseDate'
        ]


class PostImageSerializer(serializers.ModelSerializer):
    """serializer for uploading image to post."""

    class Meta:
        model = Post
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    # class Meta:
    #     fields = ['file']

