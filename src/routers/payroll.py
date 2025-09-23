from typing import Annotated

from fastapi import APIRouter, Query, Depends

from schemas import PositionListResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get(
    "/positions/",
    response_model=list[PositionListResponseSchema],
    summary="Get all positions in the company",
    description="""
    This endpoint retrieves a paginated list from the database of all position in the company.
    Clients can specify the `page` number and the number of items per page using `per_page`.
    The response is JSON file which formated using PositionListResponseSchema.
    The response includes details about the positions, total pages, and total items,
    along with links to the previous and next pages if applicable.
    """,
    responses={
        404: {
            "description": "No job positions found.",
            "content":{
                "application/json": {
                    "example": {"detail": "No job positions found."}
                }
            },
        },
    }
)
async def get_position_list(
        page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
        per_page: Annotated[int, Query(ge=1, le=20, description="Number of items per page")] = 10,
        # db: AsyncSession = Depends(get_db)    # TODO: implement get_db
):
    ...
