from pathlib import Path
from typing import Dict, Any, Optional
from parsel import Selector
from playwright.async_api import Page
from .cache_manager import load_cache, save_cache
# from ..database_manager import fetch_by_url, insert_or_replace
# from ..schema_generator import get_sheet_columns

class CacheService:
    """
    Service that coordinates caching between database and page cache.
    Implements the caching hierarchy: Database → Page Cache → Browser Fetch
    """

    def __init__(self, config_path: Path):
        self.config_path = config_path

    # def retrieve_data_from_database(self, sheet_name: str, url: str) -> Optional[Dict[str, Any]]:
    #     """
    #     Check database for persisted data for the given sheet and URL.
    #
    #     Args:
    #         sheet_name: Name of the sheet/table
    #         url: URL to check for persisted data
    #
    #     Returns:
    #         Persisted data dict if found, None otherwise
    #     """
    #     # Get URL column name for this sheet
    #     url_column = self._get_url_column_for_sheet(sheet_name)
    #     if not url_column:
    #         return None
    #
    #     # Check database for persisted data
    #     return fetch_by_url(sheet_name, url_column, url)
    #
    # def persist_data_to_database(self, sheet_name: str, data: Dict[str, Any]):
    #     """
    #     Save extracted data to database.
    #
    #     Args:
    #         sheet_name: Name of the sheet/table
    #         data: Data dict to save
    #     """
    #     insert_or_replace(sheet_name, data)

    async def get_page_selector_with_cache(self, page: Page, url: str) -> Selector:
        """
        Get page selector with hierarchical caching:
        1. Check page cache first (fastest)
        2. If not found, fetch from browser and cache

        Args:
            page: Playwright page instance
            url: URL to fetch

        Returns:
            Parsed Selector object
        """
        try:
            # Check page cache first
            cached_html = load_cache(url)
            if cached_html:
                print(f"Using cached page for {url}")
                return Selector(text=cached_html)

            # Fetch from browser
            print(f"Fetching page from browser: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            html_content = await page.content()

            # Save to page cache
            save_cache(url, html_content)

            return Selector(text=html_content)
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            # Return empty selector to prevent breaking
            return Selector(text="")

    # def _get_url_column_for_sheet(self, sheet_name: str) -> Optional[str]:
    #     """
    #     Get the URL column name for a given sheet.
    #
    #     Args:
    #         sheet_name: Name of the sheet
    #
    #     Returns:
    #         URL column name if found, None otherwise
    #     """
    #     columns = get_sheet_columns(self.config_path, sheet_name)
    #     url_columns = ['Link', 'Url']
    #
    #     for url_col in url_columns:
    #         if url_col in columns:
    #             return url_col
    #
    #     return None
