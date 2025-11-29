from pprint import pprint 
from camoufox.sync_api import Camoufox
from playwright.sync_api import Page 
from parsel import Selector
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import load_cache, save_cache 


class CarsUrlsExtractor :
    brand_new_car_template = 'https://ksa.yallamotor.com/new-cars/{brand}'

    def __init__(self,brand:str,xpath:str):
        self.__brand = brand 
        self.__xpath = xpath 
        self.__variant_urls = set()

    
    def extract_variants_urls(self) -> list[str]:
        with Camoufox(headless=True) as browser:
            page = browser.new_page()
            page_selector = self.get_page_selector(
                self.brand_new_car_template.format(brand=self.__brand),
                page
            )
            models_urls = [
                'https://ksa.yallamotor.com' + url 
                for url in page_selector.xpath('//div[contains(@data-tab,"nissan")]//a/@href').getall()
            ]
            for url in models_urls :
                page_selector = self.get_page_selector(url,page)
                new_urls = [
                        'https://ksa.yallamotor.com' + url 
                        for url in page_selector.xpath(self.__xpath).getall()
                    ]
                new_urls_source = "\n".join(new_urls)
                pprint(f'Founding new urls:\n{new_urls_source}')
                self.__variant_urls.update(new_urls)
            page.close()

    def get_variants_urls(self) -> list[str]:
        self.extract_variants_urls()
        return list(self.__variant_urls)
    
    def get_page_selector(self,url:str,page:Page) -> Selector :
        cached_html = load_cache(url)
        if cached_html:
            print(f"Using cached page for {url}")
            return Selector(text=cached_html)
        page.goto(url)
        html_content = page.content()
        save_cache(url, html_content)
        return Selector(text=html_content)
                

if __name__ == '__main__':
    extractor = CarsUrlsExtractor('nissan','//a[contains(text(),"View Detail")]/@href')
    urls = extractor.get_variants_urls()
    data = []
    with Camoufox(headless=True) as browser :
        page = browser.new_page()
        for url in urls :
            url_pipeline = Pipeline(
                url,
                [
                    BaseSheetExtractor('Engine & Power'),
                    BaseSheetExtractor('Measurements'),
                    BaseSheetExtractor('Safety Features'),
                    BaseSheetExtractor('Interior Features'),
                    BaseSheetExtractor('Exterior Features'),
                    BaseSheetExtractor('Comfort Features'),
                ],
                page 
            )
            data.append(url_pipeline.run())
    breakpoint()
