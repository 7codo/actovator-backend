from pprint import pprint
import re

from sqlmodel import Session

from app.db.base import engine
from app.services.gsc.gsc_initial import get_service

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchAnalyticsRow(BaseModel):
    keys: list[str] = Field(
        ...,
        description="The dimension values for this row (e.g., query, page, country, or device).",
    )
    clicks: int = Field(..., description="Number of clicks for this row.")
    impressions: int = Field(..., description="Number of impressions for this row.")
    ctr: float = Field(..., description="Click-through rate for this row.")
    position: float = Field(..., description="Average position for this row.")


def _extract_domain(site_url: str) -> str:
    """
    Extract the domain from a GSC siteUrl, e.g.:
    - 'sc-domain:actovator.com' -> 'actovator.com'
    - 'https://www.example.com/' -> 'www.example.com'
    """
    if site_url.startswith("sc-domain:"):
        return site_url[len("sc-domain:") :]
    # Remove protocol and trailing slash
    match = re.match(r"https?://([^/]+)/?", site_url)
    if match:
        return match.group(1)
    return site_url


def _favicon_url(domain: str) -> str:
    """
    Return a favicon URL for the given domain.
    Uses Google's favicon service.
    """
    return f"https://www.google.com/s2/favicons?domain={domain}"


def list_sites(service):
    site_list = service.sites().list().execute()
    sites = []
    for site in site_list.get("siteEntry", []):
        site_url = site.get("siteUrl", "")
        domain = _extract_domain(site_url)
        favicon_url = _favicon_url(domain)
        sites.append(
            {
                "siteUrl": site_url,
                "permissionLevel": site.get("permissionLevel"),
                "faviconUrl": favicon_url,
            }
        )
    return sites


def get_search_analytics(
    site_url: str,
    startDate: str = None,
    row_limit: int = 25000,
    service=None,
    endDate: str = None,
    dimensions: str = None,
    country_to_filter_by: Optional[str] = None,
    device_to_filter_by: Optional[str] = None,
    keyword_to_filter_by: Optional[str] = None,
    page_to_filter_by: Optional[str] = None,
) -> List[SearchAnalyticsRow]:
    """
    Fetch Google Search Console analytics data for a given site and date range.

    Parameters:
        site_url (str): The domain or URL property to query.
        row_limit (int): Maximum number of rows to return (max 25000). If None or 0, fetch all rows.
        startDate (str): Start date in YYYY-MM-DD format.
        endDate (str): End date in YYYY-MM-DD format.
        dimensions (str): Primary dimension to group by ("query", "page", "country", or "device").
        country_to_filter_by (str, optional): Filter results by country (e.g., "USA").
        device_to_filter_by (str, optional): Filter results by device ("MOBILE", "DESKTOP", "TABLET").
        keyword_to_filter_by (str, optional): Filter results by keyword/query.
        page_to_filter_by (str, optional): Filter results by page URL.

    Returns:
        List[SearchAnalyticsRow]: List of analytics rows, each with keys: 'clicks', 'ctr', 'impressions', 'keys', 'position'.
    """
    # Default to ["date"] or ["date", dimensions]
    if dimensions is None or dimensions == "date":
        dimensions_list = ["date"]
    else:
        dimensions_list = ["date", dimensions]

    # If row_limit is None or 0, fetch all rows in batches of 25000
    MAX_BATCH_SIZE = 25000
    all_rows = []
    start_row = 0

    # If row_limit is None or 0 or greater than MAX_BATCH_SIZE, do batching
    fetch_all = row_limit is None or row_limit == 0 or row_limit > MAX_BATCH_SIZE

    while True:
        # Determine batch size for this request
        batch_limit = (
            MAX_BATCH_SIZE
            if fetch_all or (row_limit is not None and row_limit > MAX_BATCH_SIZE)
            else row_limit
        )
        request = {
            "startDate": startDate,
            "endDate": endDate,
            "dimensions": dimensions_list,
            "rowLimit": batch_limit,
            "startRow": start_row,
        }

        filters = []
        if country_to_filter_by:
            filters.append({"dimension": "country", "expression": country_to_filter_by})
        if device_to_filter_by:
            filters.append({"dimension": "device", "expression": device_to_filter_by})
        if keyword_to_filter_by:
            filters.append({"dimension": "query", "expression": keyword_to_filter_by})
        if page_to_filter_by:
            filters.append({"dimension": "page", "expression": page_to_filter_by})

        if filters:
            request["dimensionFilterGroups"] = [{"filters": filters}]

        response = (
            service.searchanalytics()
            .query(siteUrl=f"sc-domain:{site_url}", body=request)
            .execute()
        )

        rows = response.get("rows", [])
        all_rows.extend(rows)

        # If we got less than batch_limit, we're done
        if len(rows) < batch_limit:
            break

        # If not fetching all, and we've reached the requested row_limit, stop
        if not fetch_all and len(all_rows) >= row_limit:
            all_rows = all_rows[:row_limit]
            break

        # Otherwise, increment start_row for next batch
        start_row += batch_limit

    return all_rows


if __name__ == "__main__":
    with Session(engine) as session:
        service = get_service("gAf7wNMxd93mxhCHqZRZIVXtgcbwNHNz", db=session)
        # sites = list_sites(service)

        result = list_sites(service)
        # sites = get_search_analytics("actovator.com", service=service)
        pprint(result, indent=3)
