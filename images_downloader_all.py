from pathlib import Path
from re import findall,sub 
from urllib.parse import quote 
import scrapy 
from scrapy.shell import inspect_response
from scrapy.utils.response import open_in_browser
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess 
from scrapy import Request 
from parsel import Selector 
from scrapy.http.response.html import HtmlResponse
import pandas as pd 

class ImageDownloader(scrapy.Spider):
    name = 'images_downloader'  
    def __init__(self):
        self._countries_images_paths = {
            'ksa':self.create_country_images_folder('ksa'),
            'uae':self.create_country_images_folder('uae')
        }
        self.dfs = pd.read_excel('output.xlsx',sheet_name=None)


    def start_requests(self):
        for _,row in self.dfs['Make Model'].iterrows():
            try :
                index = 1
                while (not pd.isna(row[f'Logo {index}'])):
                    yield Request(
                        row[f'Logo {index}'],
                        callback=self.download,
                        meta={
                            'index':index,
                            'Link':row['Link'],
                            'Slug':row['Slug']
                        }
                    )
                    index +=1 
            except KeyError :
                continue 

    def create_country_images_folder(self,country:str) -> Path:
        images_path = self.create_tree_of_folders(
            country,
            'assets',
            'img',
            'cars'
        )
        return images_path 

    def create_tree_of_folders(self,*paths:str) -> Path:
        path = Path(__file__).parents[0]
        for folder in paths :
            path = path.joinpath(folder)
            path.mkdir(exist_ok=True)
        return path
    
    def create_image_folder(self,response:HtmlResponse) -> Path:
        image_folder_path = self._countries_images_paths[
                self.get_location(response.meta['Link'])
            ].joinpath(
            self.clean_slug(response.meta['Slug'])
        )
        image_folder_path.mkdir(exist_ok=True)
        return image_folder_path
    
    def download(self,response):
        image_path = self.get_image_path(response,response.meta['index'])
        with open(image_path,'wb') as file:
            print(f'Downloading image {response.meta["index"]} for : {response.meta["Link"]}')
            file.write(response.body)


    def clean_slug(self,slug:str) -> str:
        cleaning_list = [
            '/'
        ]
        return sub('|'.join(cleaning_list),'-',slug)
    
    def get_image_path(self,response:HtmlResponse,image_id:int) -> Path:
        image_folder_path = self.create_image_folder(response)
        return image_folder_path.joinpath(f'listing_main_{str(image_id).zfill(2)}.jpg')

    def get_location(self,url:str) -> str:
        return findall('//(\S+?)\.',url)[0]

if __name__ == '__main__':  
    process = CrawlerProcess(
        {
            # 'FEEDS': {
            #     'hpc.json': {
            #         'format': 'json',
            #         'overwrite':True
            #     },
            # },
            'LOG_LEVEL':'ERROR',
            # 'CONCURRENT_REQUESTS':1,
            # 'DOWNLOAD_DELAY':3,
            'HTTPCACHE_ENABLED' : True,
            'AUTOTHROTTLE_ENABLED':True
        }
    )

    process.crawl(ImageDownloader)
    process.start()