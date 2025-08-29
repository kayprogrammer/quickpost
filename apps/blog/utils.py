from django.db.models import Count, Q
from apps.blog.models import Comment, Post


async def retrieve_post(slug: str, loaded: bool = True):
    """
    Retrieve a post by its slug.
    """
    post = Post.objects.all()
    if loaded:
        post = post.select_related("author").annotate(
            comments_count=Count("comments", filter=Q(comments__parent__isnull=True)),
            likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
            dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
        )
    post = await post.aget_or_none(slug=slug)
    return post


async def retrieve_comment(comment_id: str, loaded: bool = True):
    """
    Retrieve a comment by its id.
    """
    comment = Comment.objects.all()
    if loaded:
        comment = comment.select_related("author").annotate(
            replies_count=Count("replies"),
            likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
            dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
        )
    comment = await comment.aget_or_none(id=comment_id)
    return comment


async def retrieve_reply(reply_id: str, loaded: bool = True):
    """
    Retrieve a reply by its id.
    """
    reply = Comment.objects.all()
    if loaded:
        reply = reply.select_related("author").annotate(
            likes_count=Count("likes", filter=Q(likes__is_disliked=False)),
            dislikes_count=Count("likes", filter=Q(likes__is_disliked=True)),
        )
    reply = await reply.aget_or_none(id=reply_id)
    return reply
