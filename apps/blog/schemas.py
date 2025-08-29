from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ninja import Field, FilterSchema, ModelSchema

from apps.blog.models import Post
from apps.common.schemas import (
    BaseSchema,
    PaginatedResponseDataSchema,
    ResponseSchema,
    UserDataSchema,
)

# REQUEST SCHEMAS


class CommentCreateSchema(BaseSchema):
    text: str = Field(..., max_length=10000)


class PostCreateSchema(CommentCreateSchema):
    title: str = Field(..., max_length=200)


# FILTER & PARAMETERS SCHEMAS
class PostFilterSchema(FilterSchema):
    search: Optional[str] = Field(
        None,
        q=[
            "title__icontains",
            "author__first_name__icontains",
            "author__last_name__icontains",
            "text__icontains",
        ],
    )


class PaginationQuerySchema(BaseSchema):
    page: int = Field(1, ge=1, description="Page number for pagination")
    limit: int = Field(50, ge=1, le=100, description="Number of items per page")


# RESPONSE SCHEMAS
class BaseBlogSchema(BaseSchema):
    id: UUID
    author: UserDataSchema
    created_at: datetime
    updated_at: datetime


class PostSchema(BaseBlogSchema, ModelSchema):
    likes_count: int = Field(0)
    dislikes_count: int = Field(0)
    comments_count: int = Field(0)

    class Meta:
        model = Post
        fields = ["title", "slug", "text", "image"]


class PaginatedPostsDataSchema(PaginatedResponseDataSchema):
    posts: List[PostSchema] = Field(..., alias="items")


class PostsResponseSchema(ResponseSchema):
    data: PaginatedPostsDataSchema


class PostResponseSchema(ResponseSchema):
    data: PostSchema


class CommentSchema(BaseBlogSchema):
    text: str
    replies_count: int = Field(0)
    likes_count: int = Field(0)
    dislikes_count: int = Field(0)


class PaginatedCommentsDataSchema(PaginatedResponseDataSchema):
    comments: List[CommentSchema] = Field(..., alias="items")


class CommentsResponseSchema(ResponseSchema):
    data: PaginatedCommentsDataSchema


class CommentResponseSchema(ResponseSchema):
    data: CommentSchema


class ReplySchema(BaseBlogSchema):
    text: str
    likes_count: int = Field(0)
    dislikes_count: int = Field(0)


class PaginatedRepliesDataSchema(PaginatedResponseDataSchema):
    replies: List[ReplySchema] = Field(..., alias="items")


class RepliesResponseSchema(ResponseSchema):
    data: PaginatedRepliesDataSchema


class ReplyResponseSchema(ResponseSchema):
    data: ReplySchema


class PaginatedLikesSchema(PaginatedResponseDataSchema):
    likes_or_dislikes: List[BaseBlogSchema] = Field(..., alias="items")


class LikesResponseSchema(ResponseSchema):
    data: PaginatedLikesSchema
