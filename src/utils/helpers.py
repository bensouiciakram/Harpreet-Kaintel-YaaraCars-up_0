import asyncio 
from typing import Any 
from datetime import datetime 
from typing import Callable
from parsel import Selector 
from playwright.async_api import Browser,Page
from src.builder import SpreadsheetBuilder
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import save_cache,load_cache

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
        builder:SpreadsheetBuilder):
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
    await page.goto("about:blank", wait_until="domcontentloaded")


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
    cached_html = load_cache(url)
    if cached_html:
        print(f"Using cached page for {url}")
        return Selector(text=cached_html)
    await page.goto(url, wait_until="domcontentloaded")
    html_content = await page.content()
    save_cache(url, html_content)
    return Selector(text=html_content)

async def create_only_document_page(browser:Browser) -> Page:
    async def only_document(route, request):
        if request.resource_type == "document":
            await route.continue_()
        else:
            await route.abort()
    page = await browser.new_page()
    await page.route("**/*", only_document)
    return page 