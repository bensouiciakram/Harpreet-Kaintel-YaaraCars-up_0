from pprint import pprint 
from camoufox.sync_api import Camoufox
from playwright.sync_api import Page 
from parsel import Selector
from src.builder import SpreadsheetBuilder
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.urls_extractor import CarsUrlsExtractor
from src.utils.cache_manager import load_cache, save_cache
from src.utils.file_manager import create_output_file 
from src.utils.constants import ALL_BRAND
from src.utils.helpers import execution_time


def main():
    output_path = create_output_file()
    builder = SpreadsheetBuilder(
                    template_path=output_path
                )
    with Camoufox(headless=True) as browser :
        page = browser.new_page()
        for brand in ALL_BRAND:
            for country in ['ksa','uae']:
                extractor = CarsUrlsExtractor(country,brand,'//a[contains(text(),"View Detail")]/@href',page)
                variant_urls = extractor.get_variants_urls()
                models_urls = extractor.get_models_urls()
                for url in variant_urls :
                    url_pipeline = Pipeline(
                        url,
                        [
                            BaseSheetExtractor('Make Model'),
                            BaseSheetExtractor('Engine & Power'),
                            BaseSheetExtractor('Measurements'),
                            BaseSheetExtractor('Safety Features'),
                            BaseSheetExtractor('Interior Features'),
                            BaseSheetExtractor('Exterior Features'),
                            BaseSheetExtractor('Comfort Features'),
                        ],
                        page,
                        builder 
                    )
                    url_pipeline.run()
                for url in models_urls:
                    url_pipeline = Pipeline(
                        url,
                        [
                            BaseSheetExtractor('Description')
                        ],
                        page,
                        builder
                    )
                    url_pipeline.run()
    builder.save(output_path)   
 
if __name__ == '__main__':
    execution_time(main)
                    
