import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
from typing import Callable
from parsel import Selector
from playwright.async_api import Browser,Page
from src.builder import SpreadsheetBuilder
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from pathlib import Path
import chompjs 

def execution_time(callback,**kwargs):
    start = datetime.now()
    callback(**kwargs)
    end = datetime.now()
    duration = (end - start).seconds 
    print(f'the process last : {duration}')

async def gather_with_concurrency(n: int, *tasks: Any) -> list:
    """
    Runs async tasks with a concurrency limit.

    Args:
        n: Maximum number of concurrent tasks.
        *tasks: Awaitable tasks to run.

    Returns:
        List of results from the tasks.
    """
    semaphore = asyncio.Semaphore(n)
    async def sem_task(task: Any) -> Any:
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def extract_sheets_related_infos(
        url,
        sheets_names:list[str],
        page:Page,
        builder:SpreadsheetBuilder,
        failed_urls_container:list=None):
    try:
        from src.pipeline import Pipeline  # Local import to avoid circular dependency
        page_selector = await get_page_selector(page,url)
        url_pipeline = Pipeline(
            url,
            [
                BaseSheetExtractor(sheet_name)
                for sheet_name in sheets_names
            ],
            page_selector,
            builder
        )
        url_pipeline.run()
        # await page.goto("about:blank", wait_until="domcontentloaded")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        # Track failed URLs if container is provided
        if failed_urls_container is not None:
            failed_urls_container.append({
                'url': url,
                'error': str(e),
                'sheets': sheets_names,
                'timestamp': datetime.now().isoformat()
            })
        # Continue processing other URLs instead of breaking
        return None


async def map_execution(pages:list[Page],urls:list[str],func:Callable,**kwargs):
    tasks = [func(url,page=pages[index%len(pages)],**kwargs) for index,url in enumerate(urls)]
    # await gather_with_concurrency(len(pages),*tasks)
    batch_size = len(pages)

    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]

        tasks = [
            func(url, page=pages[j], **kwargs)
            for j, url in enumerate(batch_urls)
        ]

        # Barrier: wait for the whole batch
        await asyncio.gather(*tasks)


async def get_page_content(page:Page,url:str) -> Selector:
    await page.goto(url, wait_until="domcontentloaded")
    return Selector(text=await page.content())


async def get_page_selector(page:Page,url:str) -> Selector :
    # Initialize cache service for page-level caching
    from src.utils.cache_utils.cache_service import CacheService
    config_path = Path(__file__).parents[1].joinpath('config/config.json')
    cache_service = CacheService(config_path)
    return await cache_service.get_page_selector_with_cache(page, url)

async def create_only_document_page(browser:Browser) -> Page:
    async def only_document(route, request):
        if request.resource_type == "document":
            await route.continue_()
        else:
            await route.abort()
    page = await browser.new_page()
    await page.route("**/*", only_document)
    return page

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_data_embedded_object(page_selector:Selector,xpath:str) -> dict:
    return chompjs.parse_js_object(chompjs.parse_js_object(page_selector.xpath(xpath).get())[1])