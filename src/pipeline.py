# pipeline.py

from camoufox import Camoufox
from parsel import Selector
from src.extractor import Extractor
# from transformer import Transformer
# from validator import Validator
# from builder import SpreadsheetBuilder
# from uploader import Uploader
from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor
from src.utils.cache_manager import load_cache,save_cache

class Pipeline:
    """
    Orchestrates the full data workflow:
    Extract → Transform → Validate → Build → Upload
    """

    def __init__(self, variant_url:str, sheet_extractors, builder=None, uploader=None):
        """
        Args:
            page: parsel Selector containing the HTML content.
            sheet_extractors: List of BaseSheetExtractor instances.
            builder: Optional SpreadsheetBuilder instance.
            uploader: Optional Uploader instance.
        """
        self._page = self.get_page_selector(variant_url)
        self.extractor = Extractor(self._page, sheet_extractors)
        # self.transformer = Transformer()
        # self.validator = Validator()
        # self.builder = builder or SpreadsheetBuilder()
        # self.uploader = uploader or Uploader()

    def run(self):
        """
        Execute the full pipeline and return final data.
        """
        # 1️⃣ Extract
        raw_data = self.extractor.extract_all()
        breakpoint()

        # 2️⃣ Transform
        # transformed_data = self.transformer.transform(raw_data)

        # # 3️⃣ Validate
        # self.validator.validate(transformed_data)

        # # 4️⃣ Build spreadsheet
        # for sheet_name, sheet_data in transformed_data.items():
        #     self.builder.add_sheet(sheet_name, sheet_data)
        # file_path = self.builder.save("YallaCars_Upload.xlsx")

        # # 5️⃣ Upload
        # self.uploader.upload(file_path)

        # return transformed_data
    
    def get_page_selector(self,variant_url:str) -> Selector :
        cached_html = load_cache(variant_url)
        if cached_html:
            print(f"Using cached page for {variant_url}")
            return Selector(text=cached_html)
        with Camoufox() as browser:
            page = browser.new_page()
            page.goto(variant_url)
            html_content = page.content()
            save_cache(variant_url, html_content)
            return Selector(text=html_content)
