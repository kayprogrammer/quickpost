from ninja import Field, Schema as _Schema


class Schema(_Schema):
    class Config:
        arbitrary_types_allowed = True

        @staticmethod
        def schema_extra(schema: dict, _):
            schema["properties"] = {
                k: v
                for k, v in schema.get("properties", {}).items()
                if not v.get("hidden", False)
            }


class ResponseSchema(Schema):
    status: str = "success"
    message: str


class ErrorResponseSchema(ResponseSchema):
    status: str = "failure"


class PaginatedResponseDataSchema(Schema):
    per_page: int
    current_page: int
    last_page: int


class UserDataSchema(Schema):
    name: str = Field(..., alias="full_name")
    avatar: str = Field(None, alias="avatar_url")
