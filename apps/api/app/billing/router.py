from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import PlanOut
from app.services.billing import activate_premium, list_plans

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
async def get_plans(db: AsyncSession = Depends(get_db)) -> list[PlanOut]:
    plans = await list_plans(db)
    return [PlanOut.model_validate(p) for p in plans]


@router.get("/status")
async def billing_status(user: User = Depends(get_current_user)) -> dict:
    sub = user.subscription
    return {
        "is_premium": user.is_premium,
        "status": sub.status if sub else "none",
        "ends_at": sub.ends_at.isoformat() if sub and sub.ends_at else None,
    }


@router.post("/dev/activate-premium")
async def dev_activate(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Dev-only helper to test entitlement gates without Stars."""
    from app.core.config import get_settings

    if get_settings().environment == "production":
        raise HTTPException(status_code=403, detail="Not available in production")
    await activate_premium(db, user, stars=0, payload="dev", charge_id=f"dev-{user.id}")
    return {"ok": True, "is_premium": True}
