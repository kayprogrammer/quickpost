from uuid import UUID
from django.db.models import Count, Q
from ninja import File, Form, Query, Router, UploadedFile

from apps.blog.models import Comment, Post
from apps.blog.schemas import (
    CommentCreateSchema,
    CommentResponseSchema,
    CommentsResponseSchema,
    LikesResponseSchema,
    PaginationQuerySchema,
    PostCreateSchema,
    PostFilterSchema,
    PostResponseSchema,
    PostsResponseSchema,
    RepliesResponseSchema,
    ReplyResponseSchema,
)
from apps.blog.utils import retrieve_comment, retrieve_post, retrieve_reply
from apps.common.exceptions import ErrorCode, NotFoundError, RequestError
from apps.common.paginators import CustomPagination
from apps.common.responses import CustomResponse
from apps.common.schemas import ResponseSchema
from apps.common.utils import set_dict_attr
from apps.common.auth import AuthUser

blog_router = Router(tags=["Blog"])

paginator = CustomPagination()


# ------------------------------------------------
# POSTS ENDPOINTS
# ------------------------------------------------
@blog_router.get(
    "/posts",
    summary="Get All Posts",
    description="""
        This endpoint returns a paginated response of posts available
    """,
    response=PostsResponseSchema,
)
async def get_posts(
    request,
    page_params: Query[PaginationQuerySchema],
    filters: PostFilterSchema = Query(...),
):
    posts = Post.objects.select_related("author").annotate(
        comments_count=Count("comments", filter=Q(comments__parent__isnull=True)),
        likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
        dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
    )
    filtered_posts = filters.filter(posts)
    paginated_data = await paginator.paginate_queryset(
        filtered_posts, page_params.page, page_params.limit
    )
    return CustomResponse.success("Posts returned successfully", paginated_data)


@blog_router.post(
    "/posts",
    summary="Create Post",
    description="""
        This endpoint allows an authenticated user to create a post.
    """,
    response=PostResponseSchema,
    auth=AuthUser(),
)
async def create_post(
    request, data: Form[PostCreateSchema], image: File[UploadedFile] = None
):
    user = request.auth
    post = await Post.objects.acreate(author=user, image=image, **data.model_dump())
    return CustomResponse.success(message="Post created successfully", data=post)


@blog_router.get(
    "/posts/{slug}",
    summary="Get Single Post",
    description="""
        This endpoint returns the details of a single post
    """,
    response=PostResponseSchema,
)
async def get_post(
    request,
    slug: str,
):
    post = await retrieve_post(slug)
    if not post:
        raise NotFoundError("Post not found")
    return CustomResponse.success("Post returned successfully", post)


@blog_router.put(
    "/posts/{slug}",
    summary="Update Post",
    description="""
        This endpoint allows an authenticated user to update his/her post.
    """,
    response=PostResponseSchema,
    auth=AuthUser(),
)
async def update_post(
    request, slug: str, data: Form[PostCreateSchema], image: File[UploadedFile] = None
):

    user = request.auth
    post = await retrieve_post(slug)
    if not post:
        raise NotFoundError.error("Post not found")

    # Ensure the post belongs to the authenticated user
    if post.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER, "You are not authorized to update this post", 403
        )

    post = set_dict_attr(post, data.model_dump())
    if image:
        post.image = image
    await post.asave()
    return CustomResponse.success(message="Post updated successfully", data=post)


@blog_router.delete(
    "/posts/{slug}",
    summary="Delete Post",
    description="""
        This endpoint allows an authenticated user to delete his/her post.
    """,
    response=ResponseSchema,
    auth=AuthUser(),
)
async def delete_post(request, slug: str):
    user = request.auth
    post = await retrieve_post(slug, loaded=False)
    if not post:
        raise NotFoundError("Post not found")

    # Ensure the post belongs to the authenticated user
    if post.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER, "You are not authorized to delete this post", 403
        )

    await post.adelete()
    return CustomResponse.success(message="Post deleted successfully")


# ------------------------------------------------
# COMMENTS ENDPOINTS
# ------------------------------------------------
@blog_router.get(
    "/posts/{slug}/comments",
    summary="Get All Comments for Post",
    description="""
        This endpoint returns a paginated response of comments available
        Sort can be either 'asc' or 'desc'.
    """,
    response=CommentsResponseSchema,
)
async def get_comments(
    request, slug: str, page_params: Query[PaginationQuerySchema], sort: str = "asc"
):
    if sort and sort not in ["asc", "desc"]:
        raise RequestError(
            ErrorCode.INVALID_QUERY_PARAM, "Sort must be either 'asc' or 'desc'"
        )
    post = await retrieve_post(slug, False)
    if not post:
        raise NotFoundError("Post not found")
    comments = (
        Comment.objects.filter(post=post)
        .select_related("author")
        .annotate(
            replies_count=Count("replies"),
            likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
            dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
        )
        .order_by("created_at" if sort == "asc" else "-created_at")
    )

    paginated_data = await paginator.paginate_queryset(
        comments, page_params.page, page_params.limit
    )
    return CustomResponse.success("Comments returned successfully", paginated_data)


@blog_router.post(
    "/posts/{slug}/comments",
    summary="Create Comment",
    description="""
        This endpoint allows an authenticated user to create a comment.
    """,
    response=CommentResponseSchema,
    auth=AuthUser(),
)
async def create_comment(request, slug: str, data: CommentCreateSchema):
    user = request.auth
    post = await retrieve_post(slug, False)
    if not post:
        raise NotFoundError("Post not found")
    comment = await Comment.objects.acreate(author=user, post=post, **data.model_dump())
    return CustomResponse.success(message="Comment created successfully", data=comment)


@blog_router.get(
    "/comments/{comment_id}",
    summary="Get a single post's comment",
    description="""
        This endpoint returns a single post comment
    """,
    response=CommentResponseSchema,
)
async def get_comment(request, comment_id: UUID):
    comment = await retrieve_comment(comment_id)
    if not comment:
        raise NotFoundError("Comment not found")
    return CustomResponse.success("Comment returned successfully", comment)


@blog_router.put(
    "/comments/{comment_id}",
    summary="Update a Comment",
    description="""
        This endpoint allows an authenticated user to update his/her comment.
    """,
    response=CommentResponseSchema,
    auth=AuthUser(),
)
async def update_comment(request, comment_id: UUID, data: CommentCreateSchema):
    user = request.auth
    comment = await retrieve_comment(comment_id)
    if not comment:
        raise NotFoundError("Comment not found")
    # Ensure the comment belongs to the authenticated user
    if comment.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER,
            "You are not authorized to update this comment",
            403,
        )
    comment = set_dict_attr(comment, data.model_dump())
    await comment.asave()
    return CustomResponse.success(message="Comment updated successfully", data=comment)


@blog_router.delete(
    "/comments/{comment_id}",
    summary="Delete a Comment",
    description="""
        This endpoint allows an authenticated user to delete his/her comment.
    """,
    response=ResponseSchema,
    auth=AuthUser(),
)
async def delete_comment(request, comment_id: UUID):
    user = request.auth
    comment = await retrieve_comment(comment_id, False)
    if not comment:
        raise NotFoundError("Comment not found")
    # Ensure the comment belongs to the authenticated user
    if comment.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER,
            "You are not authorized to update this comment",
            403,
        )
    await comment.adelete()
    return CustomResponse.success(message="Comment deleted successfully")


# ------------------------------------------------
# REPLIES ENDPOINTS
# ------------------------------------------------
@blog_router.get(
    "/comments/{comment_id}/replies",
    summary="Get All Replies for a comment",
    description="""
        This endpoint returns a paginated response of replies available
        Sort can be either 'asc' or 'desc'.
    """,
    response=RepliesResponseSchema,
)
async def get_replies(
    request,
    comment_id: UUID,
    page_params: Query[PaginationQuerySchema],
    sort: str = "asc",
):
    if sort and sort not in ["asc", "desc"]:
        raise RequestError(
            ErrorCode.INVALID_QUERY_PARAM, "Sort must be either 'asc' or 'desc'"
        )
    comment = await retrieve_comment(comment_id, False)
    if not comment:
        raise NotFoundError("Comment not found")
    replies = (
        Comment.objects.filter(parent=comment)
        .select_related("author")
        .annotate(
            likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
            dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
        )
        .order_by("created_at" if sort == "asc" else "-created_at")
    )
    paginated_data = await paginator.paginate_queryset(
        replies, page_params.page, page_params.limit
    )
    return CustomResponse.success("Replies returned successfully", paginated_data)


@blog_router.post(
    "/comments/{comment_id}/replies",
    summary="Create Reply",
    description="""
        This endpoint allows an authenticated user to create a reply.
    """,
    response=CommentResponseSchema,
    auth=AuthUser(),
)
async def create_reply(request, comment_id: UUID, data: CommentCreateSchema):
    user = request.auth
    comment = await retrieve_comment(comment_id, False)
    if not comment:
        raise NotFoundError("Comment not found")
    reply = await Comment.objects.acreate(
        author=user, post_id=comment.post_id, parent=comment, **data.model_dump()
    )
    return CustomResponse.success(message="Reply created successfully", data=reply)


@blog_router.get(
    "/replies/{reply_id}",
    summary="Get a single comment's reply",
    description="""
        This endpoint returns a single comment's reply
    """,
    response=ReplyResponseSchema,
)
async def get_reply(request, reply_id: UUID):
    reply = await retrieve_reply(reply_id)
    if not reply:
        raise NotFoundError("Reply not found")
    return CustomResponse.success("Reply returned successfully", reply)


@blog_router.put(
    "/replies/{reply_id}",
    summary="Update a reply",
    description="""
        This endpoint allows an authenticated user to update his/her reply.
    """,
    response=ReplyResponseSchema,
    auth=AuthUser(),
)
async def update_reply(request, reply_id: UUID, data: CommentCreateSchema):
    user = request.auth
    reply = await retrieve_reply(reply_id)
    if not reply:
        raise NotFoundError("Reply not found")
    # Ensure the reply belongs to the authenticated user
    if reply.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER, "You are not authorized to update this reply", 403
        )
    reply = set_dict_attr(reply, data.model_dump())
    await reply.asave()
    return CustomResponse.success(message="Reply updated successfully", data=reply)


@blog_router.delete(
    "/replies/{reply_id}",
    summary="Delete a Reply",
    description="""
        This endpoint allows an authenticated user to delete his/her reply.
    """,
    response=ResponseSchema,
    auth=AuthUser(),
)
async def delete_reply(request, reply_id: UUID):
    user = request.auth
    reply = await retrieve_reply(reply_id, False)
    if not reply:
        raise NotFoundError("Reply not found")
    # Ensure the comment belongs to the authenticated user
    if reply.author_id != user.id:
        raise RequestError(
            ErrorCode.INVALID_OWNER, "You are not authorized to update this reply", 403
        )
    await reply.adelete()
    return CustomResponse.success(message="Reply deleted successfully")


# ------------------------------------------------
# LIKES/DISLIKES ENDPOINTS
# ------------------------------------------------
@blog_router.get(
    "/likes/{obj_id}",
    summary="Get Likes for a Post / Comment / Reply",
    description="""
        This endpoint returns a paginated response of likes for either a post, comment or reply.
    """,
    response=LikesResponseSchema,
)
async def get_likes_or_dislikes(
    request,
    obj_id: UUID,
    page_params: Query[PaginationQuerySchema],
    data_type: str = "post",
    is_dislike: bool = False,
):
    if data_type not in ["post", "comment", "reply"]:
        raise RequestError(
            ErrorCode.INVALID_QUERY_PARAM,
            "data_type must be either 'post', 'comment' or 'reply'",
        )

    model_objects = {"post": Post, "comment": Comment, "reply": Comment}
    model = model_objects[data_type]
    extra_filter = {"parent__isnull": True} if data_type == "comment" else {}
    object_data = await model.objects.aget_or_none(id=obj_id, **extra_filter)
    if not object_data:
        raise NotFoundError(f"{data_type.capitalize()} not found")
    likes_or_dislikes = object_data.likes.select_related("author").filter(
        is_disliked=is_dislike
    )
    paginated_data = await paginator.paginate_queryset(
        likes_or_dislikes, page_params.page, page_params.limit
    )
    return CustomResponse.success(
        "Likes/Dislikes returned successfully", paginated_data
    )


@blog_router.get(
    "/likes/{obj_id}/toggle",
    summary="Toggle Like or Dislike for a Post / Comment / Reply",
    description="""
        This endpoint allows an authenticated user to like or dislike a post, comment, or reply.  
        The obj_id represents the ID of the post, comment, or reply.
        Behavior:
        - Like → adds like
        - Like again → removes like
        - Dislike → adds dislike
        - Dislike again → removes dislike
        - Switching like/dislike → updates same record
    """,
    response=ResponseSchema,
    auth=AuthUser(),
)
async def like_or_dislike_toggle(
    request,
    obj_id: UUID,
    data_type: str = "post",
    is_dislike: bool = False,
):
    if data_type not in ["post", "comment", "reply"]:
        raise RequestError(
            ErrorCode.INVALID_QUERY_PARAM,
            "data_type must be either 'post', 'comment' or 'reply'",
        )

    model_objects = {"post": Post, "comment": Comment, "reply": Comment}
    model = model_objects[data_type]
    extra_filter = {"parent__isnull": True} if data_type == "comment" else {}
    object_data = await model.objects.aget_or_none(id=obj_id, **extra_filter)
    if not object_data:
        raise NotFoundError(f"{data_type.capitalize()} not found")

    user = request.auth
    existing_like = await object_data.likes.filter(author=user).aget_or_none()

    action = f"{'Dislike' if is_dislike else 'Like'} added"
    # CASE 1: If user already liked/disliked
    if existing_like:
        if existing_like.is_disliked == is_dislike:  # meaning it's the same button
            # Toggle off (remove)
            await existing_like.adelete()
            action = f"{'Dislike' if is_dislike else 'Like'} removed"
        else:
            # Switch like <-> dislike
            existing_like.is_disliked = is_dislike
            await existing_like.asave(update_fields=["is_disliked"])
            action = f"{'Dislike' if is_dislike else 'Like'} updated"

    else:
        # CASE 2: Create new like/dislike
        await object_data.likes.acreate(author=user, is_disliked=is_dislike)
    return CustomResponse.success(f"{action} successfully")
