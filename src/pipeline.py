# pipeline.py
from pprint import pprint 
from re import findall,split,sub
from camoufox import Camoufox
from playwright.sync_api import Page 
from parsel import Selector
from src.extractor import Extractor
from src.builder import SpreadsheetBuilder
from src.transformer import Transformer
# from transformer import Transformer
# from validator import Validator
# from uploader import Uploader
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import load_cache,save_cache


class Pipeline:
    """
    Orchestrates the full data workflow:
    Extract → Transform → Validate → Build → Upload
    """

    def __init__(self, variant_url:str, sheet_extractors:list[BaseSheetExtractor],page:Page, builder=None, uploader=None):
        """
        Args:
            page: parsel Selector containing the HTML content.
            sheet_extractors: List of BaseSheetExtractor instances.
            builder: Optional SpreadsheetBuilder instance.
            uploader: Optional Uploader instance.
        """
        self._page = page 
        self._page_selector = self.get_page_selector(variant_url)
        self.extractor = Extractor(self._page_selector, sheet_extractors)
        self.transformer = Transformer()
        # self.validator = Validator()
        # self.builder = builder or SpreadsheetBuilder()
        # self.uploader = uploader or Uploader()

    def run(self) -> dict : 
        """
        Execute the full pipeline and return final data.
        """
        # 1️⃣ Extract
        raw_data = self.extractor.extract_all()
        pprint('raw data :')
        pprint(raw_data)
        # 2️⃣ Transform
        transformed_data = self.transformer.transform(raw_data)
        # # 3️⃣ Validate
        # self.validator.validate(transformed_data)
        # # 4️⃣ Build spreadsheet
        builder = SpreadsheetBuilder(
            template_path='template - Original - Copy.xlsx'
        )
        builder.add_raw_data(transformed_data)
        file_path = builder.save("template - Original - Copy.xlsx")
        # # 5️⃣ Upload
        # self.uploader.upload(file_path)

        # return transformed_data
    
    def get_page_selector(self,variant_url:str) -> Selector :
        cached_html = load_cache(variant_url)
        if cached_html:
            print(f"Using cached page for {variant_url}")
            return Selector(text=cached_html)
        self._page.goto(variant_url)
        html_content = self._page.content()
        save_cache(variant_url, html_content)
        return Selector(text=html_content)
