from django.db import models
from autoslug import AutoSlugField
from apps.accounts.models import User
from apps.common.models import BaseModel


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from="title", unique=True, unique_with="created_at")
    text = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class Comment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    text = models.TextField()


class Like(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True
    )
    is_disliked = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "post"],
                name="unique_like_per_user_post",
            ),
            models.UniqueConstraint(
                fields=["author", "comment"],
                name="unique_like_per_user_comment",
            ),
        ]
