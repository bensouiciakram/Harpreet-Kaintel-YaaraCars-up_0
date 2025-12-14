import asyncio 
from datetime import datetime 
from camoufox.sync_api import Camoufox
from camoufox.async_api import AsyncCamoufox
from src.builder import SpreadsheetBuilder
from src.urls_extractor import CarsUrlsExtractor
from src.utils.file_manager import create_output_file 
from src.utils.constants import ALL_BRAND,VARIANTS_SHEETS_NAMES,MODELS_SHEETS_NAMES
from src.utils.helpers import execution_time,map_execution,extract_sheets_related_infos,create_only_document_page

PAGES_COUNT = 5

async def main():
    output_path = create_output_file()
    builder = SpreadsheetBuilder(
                    template_path=output_path
                )
    async with AsyncCamoufox(headless=False) as browser:
        urls_page =await create_only_document_page(browser)
        pages = [await create_only_document_page(browser) for _ in range(PAGES_COUNT)]
        for brand in ALL_BRAND:
            for country in ['ksa','uae']:
                extractor = CarsUrlsExtractor(
                    country,
                    brand,
                    '//a[contains(text(),"View Detail")]/@href',
                    urls_page,
                    2025
                )
                variant_urls = await extractor.get_variants_urls()
                models_urls = extractor.get_models_urls()
                await urls_page.goto("about:blank", wait_until="domcontentloaded")
                await map_execution(
                    pages,
                    variant_urls,
                    extract_sheets_related_infos,
                    sheets_names=VARIANTS_SHEETS_NAMES,
                    builder=builder
                )
                await map_execution(
                    pages,
                    models_urls,
                    extract_sheets_related_infos,
                    sheets_names=MODELS_SHEETS_NAMES,
                    builder=builder
                )
            builder.save(output_path) 
 
if __name__ == '__main__':
    # execution_time(main)
    start = datetime.now()
    asyncio.run(main())
    end = datetime.now()
    diff = end - start 
    print(diff.seconds)


                    
