from fastapi import APIRouter
from .sap_api import router as fast_code_router

api_router = APIRouter()
api_router.include_router(fast_code_router, prefix="/sap_api", tags=["sap_api"])
