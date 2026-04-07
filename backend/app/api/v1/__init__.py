from fastapi import APIRouter

from app.api.v1 import companies, subscriptions, briefings

router = APIRouter(prefix="/api/v1")
router.include_router(companies.router)
router.include_router(subscriptions.router)
router.include_router(briefings.router)
