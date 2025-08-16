from ninja import Field, Schema


class BaseSchema(Schema):
    class Config:
        arbitrary_types_allowed = True

        @staticmethod
        def json_schema_extra(schema: dict, _):
            schema["properties"] = {
                k: v
                for k, v in schema.get("properties", {}).items()
                if not v.get("hidden", False)
            }


class ResponseSchema(BaseSchema):
    status: str = "success"
    message: str


class ErrorResponseSchema(ResponseSchema):
    status: str = "failure"


class PaginatedResponseDataSchema(BaseSchema):
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(BaseSchema):
    name: str = Field(..., alias="full_name")
    avatar: str = Field(None, alias="avatar_url")
