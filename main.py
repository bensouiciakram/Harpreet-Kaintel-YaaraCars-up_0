from pprint import pprint 
from camoufox.sync_api import Camoufox
from playwright.sync_api import Page 
from parsel import Selector
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import load_cache, save_cache 


class CarsUrlsExtractor :
    brand_new_car_template = 'https://{country}.yallamotor.com/new-cars/{brand}'

    def __init__(self,country:str,brand:str,xpath:str,page:Page):
        self.__page = page 
        self.__country = country
        self.__brand = brand 
        self.__xpath = xpath 
        self.__variant_urls = set()
        self.__models_urls = set()

    def extract_models_urls(self):
        page_selector = self.get_page_selector(
            self.brand_new_car_template.format(
                country=self.__country,
                brand=self.__brand
            )
        )
        self.__models_urls = {
            f'https://{self.__country}.yallamotor.com' + url 
            for url in page_selector.xpath(
                f'//div[contains(@data-tab,"{self.__brand}")]//a/@href'
            ).getall()
        }
            
    
    def extract_variants_urls(self) -> list[str]:
        self.extract_models_urls()
        for url in self.__models_urls :
            page_selector = self.get_page_selector(url)
            new_urls = [
                    f'https://{self.__country}.yallamotor.com' + url 
                    for url in page_selector.xpath(self.__xpath).getall()
                ]
            new_urls_source = "\n".join(new_urls)
            pprint(f'Founding new urls:\n{new_urls_source}')
            self.__variant_urls.update(new_urls)


    def get_variants_urls(self) -> list[str]:
        self.extract_variants_urls()
        return list(self.__variant_urls)
    
    def get_models_urls(self) -> list[str]:
        return list(self.__models_urls)
    
    def get_page_selector(self,url:str) -> Selector :
        cached_html = load_cache(url)
        if cached_html:
            print(f"Using cached page for {url}")
            return Selector(text=cached_html)
        self.__page.goto(url)
        html_content = self.__page.content()
        save_cache(url, html_content)
        return Selector(text=html_content)
                
 
if __name__ == '__main__':
    with Camoufox(headless=True) as browser :
        page = browser.new_page()
        for brand in ['toyota','nissan']:
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
                        page 
                    )
                    url_pipeline.run()
                for url in models_urls:
                    url_pipeline = Pipeline(
                        url,
                        [
                            BaseSheetExtractor('Description')
                        ],
                        page 
                    )
                    url_pipeline.run()

