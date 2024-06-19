# middleware.py

from django.utils.deprecation import MiddlewareMixin
from core.models import PostInformation


class PostViewCountMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method == 'GET':
            # 'api/post/post/{id}/' where {post_id} is the post ID
            if 'api/post/post/' in request.path:
                post_id = view_kwargs.get('pk')
                if post_id:
                    try:
                        post_info = PostInformation.objects.get(
                            post_id=post_id)
                        post_info.increment_view_count()
                    except PostInformation.DoesNotExist:
                        pass
