from ninja import Router

from apps.blog.models import Post
from apps.blog.schemas import PostsResponseSchema
from apps.common.responses import CustomResponse

blog_router = Router(tags=["Blog"])


@blog_router.get(
    "/posts",
    summary="Get All Posts",
    description="""
        This endpoint returns a paginated response of posts available
    """,
    response=PostsResponseSchema,
)
async def get_posts(request):
    posts = await Post.objects.all()
    return CustomResponse.success("Posts returned successfully", posts)
