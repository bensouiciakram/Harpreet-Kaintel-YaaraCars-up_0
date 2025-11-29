# extractor.py

from src.sheet_extractors.base_sheet_extractor import BaseSheetExtractor

class Extractor:
    """
    Main Extractor class that orchestrates extraction for multiple sheets.
    """

    def __init__(self, page, sheet_extractors=None):
        """
        Args:
            page: parsel Selector containing the HTML content.
            sheet_extractors: Optional list of BaseSheetExtractor instances.
        """
        self._page = page  # private attribute
        self._sheets = sheet_extractors if sheet_extractors else []

    def add_sheet_extractor(self, sheet_extractor: BaseSheetExtractor):
        """
        Add a sheet extractor to the pipeline.

        Args:
            sheet_extractor: Instance of a sheet extractor
        """
        self._sheets.append(sheet_extractor)

    def extract_all(self):
        """
        Extract all sheets and return data as a dictionary.

        Returns:
            dict: {sheet_name: {column_name: value, ...}, ...}
        """
        data = {}
        for sheet in self._sheets:
            # Each sheet returns a dict of its columns
            data[sheet._sheet_name] = sheet.extract(self._page)
        return data
