# Performance data is available for the last 16 months. so from 2023 to 2024 will return no data

from pprint import pprint
from typing import List, Optional
from app.db.base import engine
from app.services.gsc.gsc_initial import get_service
from sqlmodel import Session
from langchain_core.tools import tool
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


def build_search_analytics_tools(service, site_url: str):
    @tool
    def get_search_analytics(
        row_limit: int = 25000,
        startDate: str = None,
        endDate: str = None,
        dimensions: str = None,
        country_to_filter_by: Optional[str] = None,
        device_to_filter_by: Optional[str] = None,
        keyword_to_filter_by: Optional[str] = None,
        page_to_filter_by: Optional[str] = None,
    ) -> List[SearchAnalyticsRow]:
        """
        Retrieve Google Search Console analytics data for a given site.

        This tool fetches search analytics data such as queries, clicks, impressions, CTR, and position
        for the specified site and date range. You can customize the results by selecting a dimension
        (e.g., "query", "page", "country", or "device") and by applying optional filters.

        Args:
            row_limit (int): Maximum number of rows to return, maximum value is 25000
            startDate (str): Start date in YYYY-MM-DD format.
            endDate (str): End date in YYYY-MM-DD format.
            dimensions (str): The primary dimension to group results by. One of "query", "page", "country", or "device".
            country_to_filter_by (str, optional): If provided, only include results for this country (e.g., "USA").
                - To find available countries for the selected date range, query with the "country" dimension first.
            device_to_filter_by (str, optional): If provided, only include results for this device (e.g., "MOBILE", "DESKTOP", "TABLET").
            keyword_to_filter_by (str, optional): If provided, only include results for this keyword/query.
                - To find available keywords for the selected date range, query with the "query" dimension first.
            page_to_filter_by (str, optional): If provided, only include results for this page URL.
                - To find available pages for the selected date range, query with the "page" dimension first.
        Returns:
            list: An array of dictionaries, each with keys: 'clicks', 'ctr', 'impressions', 'keys', 'position'.
                  Example:
                  {
                    'clicks': 236,
                    'ctr': 0.045055364642993506,
                    'impressions': 5238,
                    'keys': ['sau'],
                    'position': 18.654066437571593
                  }
        """
        dimensions = ["date", dimensions] if dimensions is not None else ["date"]
        request = {
            "startDate": startDate,
            "endDate": endDate,
            "dimensions": dimensions,
            "rowLimit": row_limit,
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
        return rows

    class _Namespace:
        pass

    ns = _Namespace()
    ns.get_search_analytics = get_search_analytics
    return ns


if __name__ == "__main__":
    with Session(engine) as session:
        service = get_service("gAf7wNMxd93mxhCHqZRZIVXtgcbwNHNz", db=session)
        # sites = list_sites(service)
        search_analytics_tools = build_search_analytics_tools(
            service, site_url="knz-ma3lomati.blogspot.com"
        )
        result = search_analytics_tools.get_search_analytics(
            startDate="2024-01-01", endDate="2025-01-01", row_limit=10
        )
        # sites = get_search_analytics("actovator.com", service=service)
        pprint(result, indent=3)
