from pprint import pprint 
from parsel import Selector 
from playwright.sync_api import Page
from src.utils.cache_utils.cache_manager import load_cache, save_cache
import chompjs 
from nested_lookup import nested_lookup
from src.utils.helpers import get_data_embedded_object 


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
        # Failed URLs tracking
        self.__failed_model_urls = []
        self.__failed_variant_urls = []

    async def extract_models_urls(self):
        try:
            page_selector = await self.get_page_selector(
                self.brand_new_car_template.format(
                    country=self.__country,
                    brand=self.__brand
                )
            )
            source = get_data_embedded_object(
                page_selector,
                '//script[contains(text(),"New Cars Make Page")]/text()'
            )
            
            # self.__models_urls = {
            #     f'https://{self.__country}.yallamotor.com' + url 
            #     for url in page_selector.xpath(
            #         # f'//div[contains(@data-tab,"{self.__brand}")]//a[contains(@href,"{self.__year}") or contains(@href,"{self.__year+1}")]/@href'
            #         f'//div[@id="{self.__brand+str(self.__year)}" or @id="{self.__brand+str(self.__year+1)}"]//a/@href'
            #     ).getall()
            # }
            self.__models_urls = {f'https://{self.__country}.yallamotor.com' + url for url in set(nested_lookup('complete_url',source))}
            models = self.__models_urls
        except Exception as e:
            print(f"Error extracting models URLs for {self.__brand} in {self.__country}: {e}")
            self.__models_urls = set()
    
    async def extract_variants_urls(self) -> list[str]:
        try:
            await self.extract_models_urls()
            for url in self.__models_urls:
                try:
                    page_selector = await self.get_page_selector(url)
                    new_urls = [
                            f'https://{self.__country}.yallamotor.com' + url 
                            for url in page_selector.xpath(self.__xpath).getall()
                        ]
                    new_urls_source = "\n".join(new_urls)
                    pprint(f'Founding new urls:\n{new_urls_source}')
                    self.__variant_urls.update(new_urls)
                except Exception as e:
                    print(f"Error extracting variant URLs from {url}: {e}")
                    # Track failed model URLs
                    self.__failed_model_urls.append({
                        'url': url,
                        'error': str(e),
                        'brand': self.__brand,
                        'country': self.__country,
                        'type': 'model'
                    })
                    continue
        except Exception as e:
            print(f"Error in extract_variants_urls for {self.__brand} in {self.__country}: {e}")

    async def get_variants_urls(self) -> list[str]:
        try:
            await self.extract_variants_urls()
            return list(self.__variant_urls)
        except Exception as e:
            print(f"Error getting variant URLs for {self.__brand} in {self.__country}: {e}")
            return []
    
    def get_models_urls(self) -> list[str]:
        try:
            return list(self.__models_urls)
        except Exception as e:
            print(f"Error getting models URLs for {self.__brand} in {self.__country}: {e}")
            return []
    
    async def get_page_selector(self,url:str) -> Selector:
        try:
            cached_html = load_cache(url)
            if cached_html: 
                print(f"Using cached page for {url}")
                return Selector(text=cached_html)
            await self.__page.goto(url)
            html_content = await self.__page.content()
            save_cache(url, html_content)
            return Selector(text=html_content)
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            # Track failed page loading
            self.__failed_model_urls.append({
                'url': url,
                'error': str(e),
                'brand': self.__brand,
                'country': self.__country,
                'type': 'page_load'
            })
            # Return empty selector to prevent breaking
            return Selector(text="")

    def get_failed_urls(self) -> dict:
        """Get all failed URLs with their error details."""
        return {
            'failed_model_urls': self.__failed_model_urls,
            'failed_variant_urls': self.__failed_variant_urls,
            'brand': self.__brand,
            'country': self.__country
        }

    def print_failed_urls_summary(self):
        """Print a summary of failed URLs."""
        failed_data = self.get_failed_urls()
        total_failed = len(failed_data['failed_model_urls']) + len(failed_data['failed_variant_urls'])
        
        if total_failed > 0:
            print(f"\n=== FAILED URLs SUMMARY FOR {self.__brand} in {self.__country} ===")
            print(f"Total failed URLs: {total_failed}")
            print(f"Failed model URLs: {len(failed_data['failed_model_urls'])}")
            print(f"Failed variant URLs: {len(failed_data['failed_variant_urls'])}")
            
            if failed_data['failed_model_urls']:
                print("\nFailed Model URLs:")
                for failed in failed_data['failed_model_urls']:
                    print(f"  - {failed['url']} | Error: {failed['error']}")
            
            if failed_data['failed_variant_urls']:
                print("\nFailed Variant URLs:")
                for failed in failed_data['failed_variant_urls']:
                    print(f"  - {failed['url']} | Error: {failed['error']}")
            print("=" * 50)
        else:
            print(f"No failed URLs for {self.__brand} in {self.__country}")
