from rest_framework import serializers
from core.models import (
    PostCategory,
    Post,
    Tag,
    SEOKeywords,
    PostRate,
    PostInformation,
    User
)
from drf_spectacular.utils import extend_schema_field


class PostCategorySerializer(serializers.ModelSerializer):
    """Serializer for postCategory"""

    parentPostCategoryId = serializers.PrimaryKeyRelatedField(
        queryset=PostCategory.objects.all(), allow_null=True, required=False
    )
    parentPostCategoryTitle = serializers.SerializerMethodField()

    class Meta:
        model = PostCategory
        fields = ['id', 'title', 'parentPostCategoryId',
                  'parentPostCategoryTitle', 'description',
                  'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': False}}

    def create(self, validated_data):
        """Create postCategory"""
        # default values
        default_status = 'Inactive'
        postCategory = PostCategory.objects.create(
            status=default_status,
            **validated_data)

        return postCategory

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_parentPostCategoryId(self, obj: object):
        if obj.parentPostCategoryId:
            return obj.parentPostCategoryId.id
        return None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_parentPostCategoryTitle(self, obj: object):
        if obj.parentPostCategoryId:
            return obj.parentPostCategoryId.title
        return None

    def update(self, instance, validated_data):
        """Update postCategory"""
        if instance.createdBy != self.context['request'].user:
            raise serializers.ValidationError(
                "You do not have permission to edit this postCategory.")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PostCategoryDetailSerializer(PostCategorySerializer):
    """Serializer for postCategory detail view."""

    class Meta(PostCategorySerializer.Meta):
        fields = PostCategorySerializer.Meta.fields + [
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


class RelatedPostsSerializer(serializers.ModelSerializer):
    """Serializer for relatedposts"""

    class Meta:
        model = Post
        fields = ['id']
        read_only_fields = ['id']


class PostInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostInformation
        fields = ['viewCount', 'socialShareCount', 'ratingCount',
                  'averageRating', 'commentCount']


class PostRateSerializer(serializers.ModelSerializer):
    """Serializer for post Rate"""

    class Meta:
        model = PostRate
        fields = ['id', 'post', 'rate']
        read_only_fields = ['id']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user
        post = data.get('post')

        # Check if we are updating an instance
        instance = self.instance

        if instance is None:
            # Only check for uniqueness on creation
            if PostRate.objects.filter(user=user, post=post).exists():
                raise serializers.ValidationError(
                    "Current user already rated this post.")
        return data

    def create(self, validated_data):
        postRate = PostRate.objects.create(**validated_data)
        return postRate

    def update(self, instance, validated_data):
        if instance.user != self.context['request'].user:
            raise serializers.ValidationError(
                "You do not have permission to edit this Post Rate.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PostUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'image']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for post"""
    tags = TagSerializer(
        many=True,
        required=False,
        help_text="""Do not send empty value.
        It must be a list (even an empty list).""")

    relatedPosts = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        many=True)

    postInformation = PostInformationSerializer(read_only=True)
    currentUserPostRate = serializers.SerializerMethodField()
    createdBy = PostUserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'postCategoryId', 'tags',
                  'postStatus', 'reviewStatus', 'isExternalSource',
                  'externalLink', 'excerpt',
                  'metaDescription', 'readTime', 'relatedPosts',
                  'image', 'createdDate', 'postInformation',
                  'currentUserPostRate', 'reviewResponseDate',
                  'createdBy']
        read_only_fields = ['id', 'reviewStatus', 'reviewResponseDate',
                            'createdBy', 'createdDate', 'postInformation']
        extra_kwargs = {'image': {'required': False}}

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_currentUserPostRate(self, obj: object):
        user = self.context['request'].user
        if user.is_authenticated and obj:
            postRate = PostRate.objects.filter(
                user=user, post=obj
                ).first()
            if postRate:
                return PostRateSerializer(postRate).data
        return None

    def _get_or_create_tags(self, tags, post):
        """Handle getting or creating tags as needed."""
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                **tag,
                defaults={'createdBy': self.context['request'].user,
                          'updatedBy': self.context['request'].user}
            )
            print('here')
            post.tags.add(tag_obj)

    def _get_related_post(self, relatedPosts, post):
        """Handle getting posts as needed."""
        for relatedPost in relatedPosts:
            related_post_obj = Post.objects.get(pk=relatedPost.id)
            post.relatedPosts.add(related_post_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        relatedPosts = validated_data.pop('relatedPosts', [])
        # by default the status of the post is draft
        validated_data['postStatus'] = 'draft'
        post = Post.objects.create(
            **validated_data)

        self._get_or_create_tags(tags, post)
        self._get_related_post(relatedPosts, post)

        return post

    def update(self, instance, validated_data):
        """Update post"""
        if instance.createdBy != self.context['request'].user:
            raise serializers.ValidationError(
                "You do not have permission to edit this post.")
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

    def validate(self, data):
        if data.get('isExternalSource') and not data.get('externalLink'):
            raise serializers.ValidationError(
                "External link must be provided for posts from external sources.")  # noqa
        return data


class PostDetailSerializer(PostSerializer):
    """Serializer for postCategory detail view."""

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            'content',
            'commentsEnabled',
            'seoKeywords'
            ]
        read_only_fields = PostSerializer.Meta.read_only_fields + [
            'createdDate',
            'commentsEnabled', 'seoKeywords',
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
