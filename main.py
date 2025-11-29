from camoufox.sync_api import Camoufox
from parsel import Selector
from src.pipeline import Pipeline
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor 


class CarsUrlsExtractor :
    brand_new_car_template = 'https://ksa.yallamotor.com/new-cars/{brand}'

    def __init__(self,brand:str,xpath:str):
        self.__brand = brand 
        self.__xpath = xpath 
        self.__variant_urls = set()

    
    def extract_variants_urls(self) -> list[str]:
        with Camoufox() as browser:
            page = browser.new_page()
            page.goto(self.brand_new_car_template.format(brand=self.__brand))
            page_selector = Selector(text=page.content())
            models_urls = [
                'https://ksa.yallamotor.com' + url 
                for url in page_selector.xpath('//div[contains(@data-tab,"nissan")]//a/@href').getall()
            ]
            page.close() 
            for url in models_urls[:1] :
                page = browser.new_page()
                page.goto(url)
                page_selector = Selector(text=page.content())
                self.__variant_urls.update(
                    [
                    'https://ksa.yallamotor.com' + url 
                    for url in page_selector.xpath(self.__xpath).getall()
                    ]
                )
                page.close()

    def get_variants_urls(self) -> list[str]:
        self.extract_variants_urls()
        return list(self.__variant_urls)
                

if __name__ == '__main__':
    extractor = CarsUrlsExtractor('nissan','//a[contains(text(),"View Detail")]/@href')
    urls = extractor.get_variants_urls()
    url = list(urls)[0]
    breakpoint()
    url_pipeline = Pipeline(
        url,
        [
            BaseSheetExtractor('Engine & Power'),
            BaseSheetExtractor('Measurements'),
            BaseSheetExtractor('Safety Features'),
            BaseSheetExtractor('Interior Features'),
            BaseSheetExtractor('Exterior Features'),
            BaseSheetExtractor('Comfort Features'),
        ]
    )


    url_pipeline.run()