from typing import Any, List
from ninja.pagination import PaginationBase
from ninja import Schema
from asgiref.sync import sync_to_async
from apps.common.exceptions import RequestError, ErrorCode
import math


class CustomPagination(PaginationBase):
    page_size = 50

    class Output(Schema):
        items: List[Any]
        total: int
        per_page: int
        current_page: int
        last_page: int

    async def paginate_queryset(self, queryset, current_page, per_page=None):
        page_size = per_page or self.page_size
        if current_page < 1:
            raise RequestError(
                err_code=ErrorCode.INVALID_PAGE,
                err_msg="Invalid Page",
                status_code=404,
            )
        async_queryset = await sync_to_async(list)(queryset)
        queryset_count = await queryset.acount()
        items = async_queryset[
            (current_page - 1) * page_size : current_page * page_size
        ]
        if queryset_count > 0 and not items:
            raise RequestError(
                err_code=ErrorCode.INVALID_PAGE,
                err_msg="Page number is out of range",
                status_code=400,
            )
        last_page = max(1, math.ceil(queryset_count / page_size))
        return {
            "items": items,
            "total": queryset_count,
            "per_page": page_size,
            "current_page": current_page,
            "last_page": last_page,
        }
