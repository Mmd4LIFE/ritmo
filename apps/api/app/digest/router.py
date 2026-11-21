from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import get_current_user
from app.core.database import get_db
from app.models.digest import DigestPrefs
from app.models.user import User
from app.schemas.common import DigestPrefsOut, DigestPrefsUpdate
from app.services.digest import compose_digest

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("/prefs", response_model=DigestPrefsOut)
async def get_prefs(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> DigestPrefsOut:
    if not user.digest_prefs:
        prefs = DigestPrefs(user_id=user.id, price_symbols=["USD/IRR"])
        db.add(prefs)
        await db.flush()
        user.digest_prefs = prefs
    return DigestPrefsOut.model_validate(user.digest_prefs)


@router.patch("/prefs", response_model=DigestPrefsOut)
async def patch_prefs(
    body: DigestPrefsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DigestPrefsOut:
    if not user.digest_prefs:
        user.digest_prefs = DigestPrefs(user_id=user.id, price_symbols=["USD/IRR"])
        db.add(user.digest_prefs)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(user.digest_prefs, k, v)
    await db.flush()
    return DigestPrefsOut.model_validate(user.digest_prefs)


@router.get("/preview")
async def preview(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    text = await compose_digest(db, user)
    return {"text": text}
