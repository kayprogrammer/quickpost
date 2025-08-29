from ninja import Field, Schema


class BaseSchema(Schema):
    class Config:
        arbitrary_types_allowed = True


class ResponseSchema(BaseSchema):
    status: str = "success"
    message: str


class ErrorResponseSchema(ResponseSchema):
    status: str = "failure"


class PaginatedResponseDataSchema(BaseSchema):
    total: int
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(BaseSchema):
    name: str = Field(..., alias="full_name")
    avatar: str = Field(None, alias="avatar_url")
