import asyncio 
from datetime import datetime 
from camoufox.sync_api import Camoufox
from camoufox.async_api import AsyncCamoufox
from src.builder import SpreadsheetBuilder
from src.urls_extractor import CarsUrlsExtractor
from src.utils.file_manager import create_output_file 
from src.utils.constants import ALL_BRAND,VARIANTS_SHEETS_NAMES,MODELS_SHEETS_NAMES
from src.utils.helpers import execution_time,map_execution,extract_sheets_related_infos,create_only_document_page

PAGES_COUNT = 1

async def main():
    try:
        output_path = create_output_file()
        builder = SpreadsheetBuilder(
                        template_path=output_path
                    )
        
        # Global failed URLs container
        global_failed_urls = []
        
        async with AsyncCamoufox(headless=False) as browser:
            urls_page =await create_only_document_page(browser)
            pages = [await create_only_document_page(browser) for _ in range(PAGES_COUNT)]
            for brand in ALL_BRAND:
                for country in ['ksa','uae']:
                    try:
                        extractor = CarsUrlsExtractor(
                            country,
                            brand,
                            '//a[button[contains(text(),"View Detail")]]/@href',
                            urls_page,
                            2025
                        )
                        variant_urls = await extractor.get_variants_urls()
                        models_urls = extractor.get_models_urls()
                        await urls_page.goto("about:blank", wait_until="domcontentloaded")
                        
                        if variant_urls:
                            print(f"Processing {len(variant_urls)} variant URLs for {brand} in {country}")
                            # Create a container for failed variant URLs
                            failed_variant_urls = []
                            await map_execution(
                                pages,
                                variant_urls,
                                extract_sheets_related_infos,
                                sheets_names=VARIANTS_SHEETS_NAMES,
                                builder=builder,
                                failed_urls_container=failed_variant_urls
                            )
                            # Add to global failed URLs
                            global_failed_urls.extend(failed_variant_urls)
                        else:
                            print(f"No variant URLs found for {brand} in {country}")
                        
                        if models_urls:
                            print(f"Processing {len(models_urls)} model URLs for {brand} in {country}")
                            # Create a container for failed model URLs
                            failed_model_urls = []
                            await map_execution(
                                pages,
                                models_urls,
                                extract_sheets_related_infos,
                                sheets_names=MODELS_SHEETS_NAMES,
                                builder=builder,
                                failed_urls_container=failed_model_urls
                            )
                            # Add to global failed URLs
                            global_failed_urls.extend(failed_model_urls)
                        else:
                            print(f"No model URLs found for {brand} in {country}")
                        
                        # Print failed URLs summary for this brand/country
                        extractor.print_failed_urls_summary()
                            
                    except Exception as e:
                        print(f"Error processing {brand} in {country}: {e}")
                        continue
                builder.save(output_path)
            
            # Print final summary of all failed URLs
            if global_failed_urls:
                print(f"\n=== FINAL FAILED URLs SUMMARY ===")
                print(f"Total failed URLs across all brands/countries: {len(global_failed_urls)}")
                print("\nFailed URLs Details:")
                for failed in global_failed_urls:
                    print(f"  - URL: {failed['url']}")
                    print(f"    Error: {failed['error']}")
                    print(f"    Sheets: {failed['sheets']}")
                    print(f"    Timestamp: {failed['timestamp']}")
                    print()
                print("=" * 50)
            else:
                print("\nNo failed URLs across all processing!")
                
    except Exception as e:
        print(f"Critical error in main execution: {e}")
        raise
 
if __name__ == '__main__':
    # execution_time(main)
    start = datetime.now()
    asyncio.run(main())
    end = datetime.now()
    diff = end - start 
    print(diff.seconds)


                    
