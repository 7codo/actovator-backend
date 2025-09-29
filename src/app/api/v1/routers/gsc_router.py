import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.v1.dependencies import get_sqlmodel_session, verify_session_token
from app.services.gsc.gsc_initial import get_service
from typing import Optional
from app.services.gsc.search_analytics import get_search_analytics, list_sites

# Use structlog's get_logger (structlog is configured in main.py)
logger = structlog.get_logger()

gsc_router = APIRouter(prefix="/gsc", tags=["gsc"])


@gsc_router.get(
    "/sites", summary="List user's GSC sites with favicon", response_model=list[dict]
)
def get_user_sites(
    session=Depends(verify_session_token),
    db: Session = Depends(get_sqlmodel_session),
):
    """
    Fetch the user's Google Search Console sites (siteUrl and faviconUrl).
    """
    user_id = session.user_id
    try:
        service = get_service(user_id, db=db)
        sites = list_sites(service)
        logger.info("Fetched GSC sites", user_id=user_id, site_count=len(sites))
        return sites
    except Exception as e:
        logger.error("Failed to fetch GSC sites", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch GSC sites: {e}",
        )


@gsc_router.get(
    "/search-analytics",
    summary="Get Google Search Console search analytics data",
    response_model=list[dict],
)
def search_analytics(
    site_url: str,
    row_limit: int = 25000,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    dimensions: Optional[str] = None,
    country_to_filter_by: Optional[str] = None,
    device_to_filter_by: Optional[str] = None,
    keyword_to_filter_by: Optional[str] = None,
    page_to_filter_by: Optional[str] = None,
    session=Depends(verify_session_token),
    db: Session = Depends(get_sqlmodel_session),
):
    """
    Retrieve Google Search Console analytics data for a given site.

    This endpoint fetches search analytics data such as queries, clicks, impressions, CTR, and position
    for the specified site and date range. You can customize the results by selecting a dimension
    (e.g., "query", "page", "country", or "device") and by applying optional filters.
    """
    user_id = session.user_id
    try:
        service = get_service(user_id, db=db)
        rows = get_search_analytics(
            site_url=site_url,
            row_limit=row_limit,
            startDate=startDate,
            endDate=endDate,
            dimensions=dimensions,
            country_to_filter_by=country_to_filter_by,
            device_to_filter_by=device_to_filter_by,
            keyword_to_filter_by=keyword_to_filter_by,
            page_to_filter_by=page_to_filter_by,
            service=service,
        )
        logger.info(
            "Fetched search analytics",
            user_id=user_id,
            site_url=site_url,
            row_count=len(rows),
            dimensions=dimensions,
            filters={
                "country": country_to_filter_by,
                "device": device_to_filter_by,
                "keyword": keyword_to_filter_by,
                "page": page_to_filter_by,
            },
        )
        return rows
    except Exception as e:
        logger.error(
            "Failed to fetch search analytics",
            user_id=user_id,
            site_url=site_url,
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch search analytics: {e}",
        )
