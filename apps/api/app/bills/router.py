from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.bill import Bill
from app.models.user import User
from app.schemas.common import BillCreate, BillOut, BillUpdate
from app.services.bills import create_bill, list_bills, mark_paid

router = APIRouter(prefix="/api/bills", tags=["bills"])


@router.get("", response_model=list[BillOut])
async def get_bills(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> list[BillOut]:
    bills = await list_bills(db, user)
    return [BillOut.model_validate(b) for b in bills]


@router.post("", response_model=BillOut)
async def post_bill(
    body: BillCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillOut:
    bill = await create_bill(db, user, body.model_dump())
    return BillOut.model_validate(bill)


@router.patch("/{bill_id}", response_model=BillOut)
async def patch_bill(
    bill_id: UUID,
    body: BillUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillOut:
    result = await db.execute(select(Bill).where(Bill.id == bill_id, Bill.user_id == user.id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(bill, k, v)
    await db.flush()
    return BillOut.model_validate(bill)


@router.post("/{bill_id}/paid", response_model=BillOut)
async def post_paid(
    bill_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillOut:
    try:
        bill = await mark_paid(db, user, bill_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Bill not found") from None
    return BillOut.model_validate(bill)


@router.delete("/{bill_id}")
async def delete_bill(
    bill_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Bill).where(Bill.id == bill_id, Bill.user_id == user.id))
    bill = result.scalar_one_or_none()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.is_active = False
    await db.flush()
    return {"ok": True}
