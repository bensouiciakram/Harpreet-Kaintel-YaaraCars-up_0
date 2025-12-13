from pprint import pprint 
from camoufox.sync_api import Camoufox
from playwright.sync_api import Page,sync_playwright
from parsel import Selector
from src.builder import SpreadsheetBuilder
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.urls_extractor import CarsUrlsExtractor
from src.utils.cache_manager import load_cache
from src.utils.file_manager import create_output_file 
from src.utils.constants import ALL_BRAND,VARIANTS_SHEETS_NAMES,MODELS_SHEETS_NAMES
from src.utils.helpers import execution_time,extract_sheets_related_infos,map_execution


def main():
    output_path = create_output_file()
    builder = SpreadsheetBuilder(
                    template_path=output_path
                )
    with Camoufox(headless=True) as browser :
        page = browser.new_page()
        for brand in ALL_BRAND:
            for country in ['ksa','uae']:
                extractor = CarsUrlsExtractor(country,brand,'//a[contains(text(),"View Detail")]/@href',page,2025)
                variant_urls = extractor.get_variants_urls()
                models_urls = extractor.get_models_urls()
                page.goto("about:blank")
                map_execution(
                    variant_urls,
                    extract_sheets_related_infos,
                    sheets_names=VARIANTS_SHEETS_NAMES,
                    page=page,
                    builder=builder
                )
                map_execution(
                    models_urls,
                    extract_sheets_related_infos,
                    sheets_names=MODELS_SHEETS_NAMES,
                    page=page,
                    builder=builder
                )
            builder.save(output_path) 
 
if __name__ == '__main__':
    execution_time(main)
                    
