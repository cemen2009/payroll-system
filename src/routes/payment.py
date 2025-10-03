from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from crud import count_entities, fetch_payments, fetch_payment_by_id, create_payment_entity
from exceptions import NotFoundEntityException, ConflictEntityException, BadRequestException
from models import PaymentModel
from schemas import PaymentListResponseSchema, PaymentDetailResponseSchema, PaymentCreateRequestSchema

router = APIRouter()


@router.get(
    "/",
    response_model=PaymentListResponseSchema,
    summary="Get list of payments payments.",
)
async def get_payments(
        page: Annotated[int, Query()] = 1,
        per_page: Annotated[int, Query()] = 10,
        db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * per_page

    total = await count_entities(PaymentModel, db)
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payments were found."
        )

    payments = await fetch_payments(offset, per_page, db)
    response = PaymentListResponseSchema(total=total, items=payments)
    return response


@router.get(
    "/{payment_id}/",
    response_model=PaymentDetailResponseSchema,
    summary="Get payment instance by ID.",
)
async def get_payment(
        payment_id: Annotated[int, Path()],
        db: AsyncSession = Depends(get_db)
):
    try:
        payment = await fetch_payment_by_id(payment_id, db)
    except NotFoundEntityException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.msg
        )

    return payment


@router.post(
    "/",
    response_model=PaymentDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new payment.",
)
async def create_payment(
        data: Annotated[PaymentCreateRequestSchema, Body()],
        db: AsyncSession = Depends(get_db)
):
    try:
        return await create_payment_entity(data, db)
    except ConflictEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.msg)
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
