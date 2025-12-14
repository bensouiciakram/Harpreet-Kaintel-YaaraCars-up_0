import shutil 
from pprint import pprint 
from pathlib import Path 
from re import findall,split,sub
from playwright.sync_api import Page 
from parsel import Selector
from src.extractor import Extractor
from src.builder import SpreadsheetBuilder
from src.transformer import Transformer
from src.images_downloader import ImagesDownloader
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import load_cache,save_cache


class Pipeline:
    """
    Orchestrates the full data workflow:
    Extract → Transform → Images Download → Build 
    """

    def __init__(
            self,
            variant_url:str,
            sheet_extractors:list[BaseSheetExtractor],
            page_selector:Selector,
            builder:SpreadsheetBuilder=None,
            uploader=None):
        """
        Args:
            page: parsel Selector containing the HTML content.
            sheet_extractors: List of BaseSheetExtractor instances.
            builder: Optional SpreadsheetBuilder instance.
            uploader: Optional Uploader instance.
        """
        self._page_selector = page_selector
        # self._page_selector = self.get_page_selector(variant_url)
        self.extractor = Extractor(self._page_selector, sheet_extractors)
        self.transformer = Transformer()
        self.image_downloader = ImagesDownloader()
        self.builder = builder 

        # self.validator = Validator()

    def run(self) -> dict : 
        """
        Execute the full pipeline and return final data.
        """
        # 1️⃣ Extract
        raw_data = self.extractor.extract_all()
        print('item extracted')
        # 2️⃣ Transform
        transformed_data = self.transformer.transform(raw_data)

        # # 3️⃣ Image download
        # self.image_downloader.download(transformed_data)
        
        # # 4️⃣ add data into spreadsheet
        self.builder.add_raw_data(transformed_data)

        return transformed_data
    
    

        
