from fastapi import APIRouter

from app.api.v1 import auth, briefings, companies, subscriptions, users

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)       # POST /api/v1/auth/signup, /auth/login
router.include_router(users.router)      # GET  /api/v1/users/me
router.include_router(companies.router)  # GET  /api/v1/companies/...
router.include_router(subscriptions.router)  # GET/POST/DELETE /api/v1/subscriptions
router.include_router(briefings.router)  # GET  /api/v1/briefings/today
