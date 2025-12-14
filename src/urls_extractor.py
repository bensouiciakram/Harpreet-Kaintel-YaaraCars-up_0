from pprint import pprint 
from parsel import Selector 
from playwright.sync_api import Page
from src.utils.cache_manager import load_cache, save_cache 


class CarsUrlsExtractor :
    brand_new_car_template = 'https://{country}.yallamotor.com/new-cars/{brand}'

    def __init__(self,country:str,brand:str,xpath:str,page:Page,year:int):
        self.__page = page 
        self.__country = country
        self.__brand = brand 
        self.__xpath = xpath 
        self.__variant_urls = set()
        self.__models_urls = set()
        self.__year = year 

    async def extract_models_urls(self):
        page_selector = await self.get_page_selector(
            self.brand_new_car_template.format(
                country=self.__country,
                brand=self.__brand
            )
        )
        self.__models_urls = {
            f'https://{self.__country}.yallamotor.com' + url 
            for url in page_selector.xpath(
                # f'//div[contains(@data-tab,"{self.__brand}")]//a[contains(@href,"{self.__year}") or contains(@href,"{self.__year+1}")]/@href'
                f'//div[@id="{self.__brand+str(self.__year)}" or @id="{self.__brand+str(self.__year+1)}"]//a/@href'
            ).getall()
        }
    
    async def extract_variants_urls(self) -> list[str]:
        await self.extract_models_urls()
        for url in self.__models_urls :
            page_selector = await self.get_page_selector(url)
            new_urls = [
                    f'https://{self.__country}.yallamotor.com' + url 
                    for url in page_selector.xpath(self.__xpath).getall()
                ]
            new_urls_source = "\n".join(new_urls)
            pprint(f'Founding new urls:\n{new_urls_source}')
            self.__variant_urls.update(new_urls)


    async def get_variants_urls(self) -> list[str]:
        await self.extract_variants_urls()
        return list(self.__variant_urls)
    
    def get_models_urls(self) -> list[str]:
        return list(self.__models_urls)
    
    async def get_page_selector(self,url:str) -> Selector :
        cached_html = load_cache(url)
        if cached_html: 
            print(f"Using cached page for {url}")
            return Selector(text=cached_html)
        await self.__page.goto(url)
        html_content = await self.__page.content()
        save_cache(url, html_content)
        return Selector(text=html_content)