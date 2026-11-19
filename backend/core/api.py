from ninja import NinjaAPI
from api.api import router as proposal_router, auth_router

api = NinjaAPI(
    title="Proposal SaaS API",
    version="1.0.0",
    description="Backend API for managing and generating commercial proposals."
)

api.add_router("/auth", auth_router)
api.add_router("/proposals", proposal_router)

@api.get("/health", tags=["System"])
def health_check(request):
    return {"status": "ok", "message": "Service is healthy"}
