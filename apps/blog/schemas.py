from typing import List, Optional
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


# FILTER SCHEMAS
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


# RESPONSE SCHEMAS
class PostSchema(ModelSchema):
    author: UserDataSchema
    likes_count: int
    dislikes_count: int
    comments_count: int

    class Meta:
        model = Post
        fields = ["title", "slug", "text", "image"]


class PaginatedPostsDataSchema(PaginatedResponseDataSchema):
    posts: List[PostSchema] = Field(..., alias="items")


class PostsResponseSchema(ResponseSchema):
    data: PaginatedPostsDataSchema


class CommentSchema(ModelSchema):
    author: UserDataSchema
    text: str
    replies_count: int


class PaginatedCommentsDataSchema(PaginatedResponseDataSchema):
    items: List[CommentSchema]


class PostDetailWithCommentsDataSchema(PostSchema):
    comments: PaginatedCommentsDataSchema


class PostDetailResponseSchema(ResponseSchema):
    data: PostDetailWithCommentsDataSchema


class ReplySchema(BaseSchema):
    author: UserDataSchema
    text: str


class PaginatedRepliesDataSchema(PaginatedResponseDataSchema):
    replies: List[ReplySchema] = Field(..., alias="items")


class RepliesResponseSchema(ResponseSchema):
    data: PaginatedRepliesDataSchema


class PaginatedLikesSchema(PaginatedResponseDataSchema):
    users: List[UserDataSchema]
